# DeepAgents Chat POC

一个轻量级智能对话系统 POC。前端使用 Vue + Vite，后端使用 Python + FastAPI + DeepAgents，支持 OpenAI 兼容模型配置、SSE 流式输出、按需加载 Skill、从文件加载 agent system prompt，并在前端展示可观察的执行过程。

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
MODEL_ID=gpt-4o-mini
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_API_KEY=your-api-key
MODEL_TEMPERATURE=0.7
CORS_ORIGINS=http://127.0.0.1:5173
SKILLS_ENABLED=true
SKILLS_DIR=skills
SYSTEM_PROMPT_PATH=prompts/system.md
```

说明：

- `MODEL_ID`: 模型 ID，例如 OpenAI 或 DeepSeek 的 OpenAI 兼容模型名。
- `MODEL_BASE_URL`: OpenAI 兼容接口地址。
- `MODEL_API_KEY`: 模型 API key，请只写在本地 `.env` 中。
- `SKILLS_DIR`: Skill 目录，默认从项目根目录下的 `skills/` 加载。
- `SYSTEM_PROMPT_PATH`: agent system prompt 文件路径，默认 `prompts/system.md`。

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

## 项目目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI 路由，包含会话、健康检查、skill metadata API
│   │   ├── chat/                # 对话核心逻辑、DeepAgents runner、SSE 事件、schema
│   │   ├── skills/              # Skill metadata 加载与目录解析
│   │   ├── storage/             # 内存会话与消息存储
│   │   ├── config.py            # 环境变量配置
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
