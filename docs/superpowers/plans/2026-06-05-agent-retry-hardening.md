# Agent Retry Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bounded agent retries and harden backend edge cases without changing public API paths.

**Architecture:** Add a retry runner that wraps the existing lazy DeepAgents runner. ChatService keeps SSE failure conversion, storage exposes explicit missing-message errors, and skill discovery skips bad files with warnings.

**Tech Stack:** Python, FastAPI, DeepAgents, pytest.

---

### Task 1: Retry Runner

**Files:**
- Create: `backend/app/chat/retry.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/chat/service.py`
- Test: `backend/tests/test_agent_retry.py`
- Test: `backend/tests/test_chat_service.py`

- [ ] Add `AGENT_MAX_RETRIES` setting with default `3`.
- [ ] Add `RetryingAgentRunner`.
- [ ] Retry only if no assistant `delta` has been emitted.
- [ ] Return a Chinese retry failure message after exhaustion.

### Task 2: Backend Edge Cases

**Files:**
- Modify: `backend/app/storage/conversations.py`
- Modify: `backend/app/skills/loader.py`
- Test: `backend/tests/test_storage.py`
- Test: `backend/tests/test_skills_loader.py`

- [ ] Add `UnknownMessageError`.
- [ ] Lock direct conversation reads.
- [ ] Skip bad skill files with warning logs.

### Task 3: Verification

**Files:**
- Modify: `openspec/changes/add-agent-retry-hardening/tasks.md`

- [ ] Run `backend/.venv/bin/pytest backend/tests`.
- [ ] Run `npm run build` from `frontend`.
- [ ] Restart backend and confirm health endpoint.
