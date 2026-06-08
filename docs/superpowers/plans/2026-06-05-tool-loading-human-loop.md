# Tool Loading Human Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local tool loading and a file-write human approval framework for the DeepAgents chat backend.

**Architecture:** Add focused `tools` and `human_loop` backend packages. Tool loader reads metadata and imports `get_tool()` from local tool modules. DeepAgentRunner receives loaded tools and interrupt policies. Approval APIs manage pending approvals in memory and leave a clean extension point for future LangGraph resume support.

**Tech Stack:** Python, FastAPI, DeepAgents, LangChain tools, Vue.

---

### Task 1: Backend Tool Loading

**Files:**
- Create: `backend/app/tools/schemas.py`
- Create: `backend/app/tools/loader.py`
- Create: `backend/app/api/tools.py`
- Create: `tools/current-time/TOOL.md`
- Create: `tools/current-time/tool.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/main.py`

- [ ] Load valid tools from `TOOLS_DIR`.
- [ ] Skip invalid tools with warning logs.
- [ ] Expose `GET /api/tools`.

### Task 2: Human Loop Framework

**Files:**
- Create: `backend/app/human_loop/config.py`
- Create: `backend/app/human_loop/schemas.py`
- Create: `backend/app/human_loop/store.py`
- Create: `backend/app/api/human_loop.py`
- Modify: `backend/app/chat/events.py`
- Modify: `backend/app/chat/agent.py`
- Modify: `backend/app/api/router.py`

- [ ] Configure `write_file` and `edit_file` approval policies.
- [ ] Add approval APIs.
- [ ] Map approval-required stream events.

### Task 3: Frontend and Verification

**Files:**
- Modify: `frontend/src/api/chat.js`
- Modify: `frontend/src/components/ChatShell.vue`
- Modify: `frontend/src/components/MessageList.vue`
- Modify: `frontend/src/styles.css`
- Modify: `README.md`
- Modify: `backend/README.md`
- Modify: `openspec/changes/add-tool-loading-human-loop/tasks.md`

- [ ] Display tool count and approval-required events.
- [ ] Document tool loading and HITL.
- [ ] Run backend tests and frontend build.
