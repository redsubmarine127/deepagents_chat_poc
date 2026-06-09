# DeepAgents Chat POC

一个轻量级智能对话系统 POC。前端使用 Vue + Vite，后端使用 Python + FastAPI + DeepAgents，支持 OpenAI 兼容模型配置、SSE 流式输出、按需加载 Skill、从文件加载 agent system prompt、本地 tool 加载，以及基于内存 checkpoint 的 human-in-the-loop 审批恢复流程。

## 技术栈

- Frontend: Vue 3, Vite
- Backend: Python 3.11+, FastAPI, DeepAgents, LangChain OpenAI
- Model: OpenAI-compatible chat model API
- Spec: OpenSpec
- Runtime ports:
  - Frontend: `http://127.0.0.1:5173`
  - Backend: `http://127.0.0.1:8090`

## 快速启动

### 1. 配置后端环境

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

编辑 `backend/.env`，填写模型配置：

```env
APP_NAME=DeepAgents Chat
MODEL_ID=gpt-4o-mini
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_API_KEY=your-api-key
MODEL_TEMPERATURE=0.7
CORS_ORIGINS=http://127.0.0.1:5173,http://127.0.0.1:5174
SKILLS_ENABLED=true
SKILLS_DIR=skills
SYSTEM_PROMPT_PATH=prompts/system.md
AGENT_MAX_RETRIES=3
TOOLS_ENABLED=true
TOOLS_DIR=tools
HUMAN_LOOP_ENABLED=false
```

说明：

- `APP_NAME`: FastAPI 应用名称，默认 `DeepAgents Chat`。
- `MODEL_ID`: 模型 ID，例如 OpenAI 或 DeepSeek 的 OpenAI 兼容模型名。
- `MODEL_BASE_URL`: OpenAI 兼容接口地址。
- `MODEL_API_KEY`: 模型 API key，请只写在本地 `.env` 中。
- `MODEL_TEMPERATURE`: 模型温度，默认 `0.7`。
- `CORS_ORIGINS`: 允许访问后端的前端地址，多个地址用英文逗号分隔。
- `SKILLS_ENABLED`: 是否启用 Skill 加载，默认 `true`。
- `SKILLS_DIR`: Skill 目录，默认从项目根目录下的 `skills/` 加载。
- `SYSTEM_PROMPT_PATH`: agent system prompt 文件路径，默认 `prompts/system.md`。
- `AGENT_MAX_RETRIES`: Agent 执行失败时的最大尝试次数，默认 `3`。
- `TOOLS_ENABLED`: 是否加载本地 tool，默认 `true`。
- `TOOLS_DIR`: Tool 目录，默认从项目根目录下的 `tools/` 加载。
- `HUMAN_LOOP_ENABLED`: 是否启用 `write_file`、`edit_file` 的人工审批中断，默认 `false`。

### 2. 启动后端

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
```

健康检查：

```bash
curl http://127.0.0.1:8090/api/health
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:5173
```

## 测试与构建

后端测试：

```bash
backend/.venv/bin/pytest backend/tests
```

前端构建：

```bash
cd frontend
npm run build
```

## Tool 与 Human-in-the-loop

Tool 默认从 `tools/` 目录加载。每个 tool 使用一个子目录，包含：

```text
tools/
└── example-tool/
    ├── TOOL.md   # name/description metadata
    └── tool.py   # get_tool() returns a LangChain-compatible tool
```

后端启动时会通过一次 catalog 扫描同时得到 tool metadata 和可执行 tool 实例：

- `GET /api/tools` 返回已发现的 tool metadata。
- 有效 tool 会传入 DeepAgents。
- Tool metadata 包含 `available` 和 `loadError`，坏 tool 会标记为不可用、写入 warning 日志，并不会阻塞其他 tool。

Human-in-the-loop 当前是进程内存版，默认关闭：

- 设置 `HUMAN_LOOP_ENABLED=true` 后，DeepAgents 才会对 `write_file`、`edit_file` 配置人工审批。
- 默认 `HUMAN_LOOP_ENABLED=false` 时，后端不会向 DeepAgents 传入 `interrupt_on`，写入类工具不会触发审批中断。
- 触发 interrupt 时，后端会创建 approval 记录并向前端发送 `approval_required` SSE 事件。
- 前端 Approvals 菜单展示 pending approval，点击 approve/reject 后会调用审批续跑 SSE 端点。
- 后端使用 LangGraph `InMemorySaver`，因此审批恢复只保证当前后端进程生命周期内可用。

## 运行日志

后端使用 Python 标准 `logging` 输出运维日志，启动后可直接在 uvicorn 终端查看。当前日志覆盖：

- 对话请求开始、上下文数量、流式输出片段、完成和失败。
- DeepAgents 初始化、模型流式输出、工具调用开始和结束。
- Skill 目录解析、缺失目录、发现的 skill 数量和 skill id。
- Tool catalog 解析、坏 tool 跳过、approval 创建与审批恢复。

日志会对长文本做截断摘要，并对 payload 中的 `api_key`、`token`、`secret`、`password` 等敏感字段脱敏。

## 项目目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI 路由，包含会话、健康检查、skill metadata API
│   │   ├── chat/                # 对话核心逻辑、DeepAgents runner、SSE 事件、schema
│   │   ├── human_loop/          # 内存审批 store、schema、HITL 配置
│   │   ├── skills/              # Skill metadata 加载与目录解析
│   │   ├── storage/             # 内存会话与消息存储
│   │   ├── tools/               # Tool metadata 与执行模块加载
│   │   ├── config.py            # 环境变量配置
│   │   ├── runtime.py           # 运行时依赖组装
│   │   └── main.py              # FastAPI 应用入口
│   ├── tests/                   # 后端 pytest 测试
│   ├── .env.example             # 后端环境变量模板
│   ├── pyproject.toml           # 后端依赖与 pytest 配置
│   └── README.md                # 后端单独启动说明
├── frontend/
│   ├── src/
│   │   ├── api/                 # 前端 API 与 SSE 流读取
│   │   ├── components/          # ChatShell、MessageList、MessageInput
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── skills/
│   ├── README.md
│   └── requirement-analysis/    # 示例 Skill
├── prompts/
│   └── system.md                # agent system prompt
├── tools/
│   ├── README.md
│   └── current-time/            # 示例 Tool
├── openspec/
│   ├── specs/                   # 当前能力规格
│   └── changes/                 # 每次需求调整记录
├── docs/
│   └── superpowers/             # 设计与实施计划文档
└── README.md
```

## Skill 与 System Prompt

Skill 默认从 `skills/` 目录加载，每个 Skill 使用一个子目录和 `SKILL.md` 文件：

```text
skills/
└── example-skill/
    └── SKILL.md
```

System prompt 默认从 `prompts/system.md` 读取，可通过 `SYSTEM_PROMPT_PATH` 修改。

## OpenSpec

需求调整记录在 `openspec/changes/` 下。修改功能或行为前，建议先阅读：

```text
openspec/project.md
openspec/specs/chat/spec.md
openspec/changes/
```
