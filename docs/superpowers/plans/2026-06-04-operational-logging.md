# Operational Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add useful backend operational logs for chat, model streaming, tools, and skills without leaking secrets or unbounded content.

**Architecture:** Add one small `app.observability` helper for text and payload summaries. Use module loggers in chat service, DeepAgents runner, and skill loader. Keep all logs on Python standard logging and configure the `app` logger at startup.

**Tech Stack:** Python logging, FastAPI, pytest `caplog`.

---

### Task 1: Safe Log Summaries

**Files:**
- Create: `backend/app/observability.py`
- Test: `backend/tests/test_observability.py`

- [ ] Add `summarize_text` and `summarize_payload`.
- [ ] Redact sensitive payload keys and truncate long text.
- [ ] Verify summaries do not include full long content.

### Task 2: Chat and Agent Logs

**Files:**
- Modify: `backend/app/chat/service.py`
- Modify: `backend/app/chat/agent.py`
- Modify: `backend/app/skills/loader.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_chat_service.py`
- Test: `backend/tests/test_agent_skills.py`
- Test: `backend/tests/test_skills_loader.py`

- [ ] Log chat start, history size, output chunks, completion, and failures.
- [ ] Log DeepAgents initialization and tool start/end events.
- [ ] Log skill directory resolution and discovery.
- [ ] Configure `app` logger to INFO during app startup.

### Task 3: Verification

**Files:**
- Modify: `openspec/changes/add-operational-logging/tasks.md`

- [ ] Run `backend/.venv/bin/pytest backend/tests`.
- [ ] Run `npm run build` from `frontend`.
- [ ] Restart backend and confirm logs print to stdout.
