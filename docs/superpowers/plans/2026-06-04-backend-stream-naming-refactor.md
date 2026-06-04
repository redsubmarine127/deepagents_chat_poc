# Backend Stream Naming Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce duplicated and ambiguous backend naming while preserving the existing chat API and SSE behavior.

**Architecture:** Add a small stream event module for chat event types and builders. Reuse one skill directory resolver for both DeepAgents setup and skill metadata discovery. Keep comments focused on the two non-obvious boundaries: DeepAgents raw event mapping and non-persistent reasoning traces.

**Tech Stack:** Python, FastAPI, DeepAgents, pytest, OpenSpec.

---

### Task 1: Stream Event Types

**Files:**
- Create: `backend/app/chat/events.py`
- Modify: `backend/app/chat/service.py`
- Modify: `backend/app/chat/agent.py`
- Test: `backend/tests/test_chat_service.py`
- Test: `backend/tests/test_agent_skills.py`

- [ ] Create `ChatStreamEventType`, `ChatStreamEvent`, and builder functions for `started`, `reasoning`, `delta`, `completed`, and `failed`.
- [ ] Replace stringly typed event creation in `ChatService`.
- [ ] Replace DeepAgents mapper return literals with event builders.
- [ ] Run `backend/.venv/bin/pytest backend/tests/test_chat_service.py backend/tests/test_agent_skills.py`.

### Task 2: Skill Directory Resolution

**Files:**
- Modify: `backend/app/skills/loader.py`
- Modify: `backend/app/chat/agent.py`
- Test: `backend/tests/test_skills_loader.py`
- Test: `backend/tests/test_agent_skills.py`

- [ ] Add shared skill directory resolution in `backend/app/skills/loader.py`.
- [ ] Use the resolver from both skill discovery and DeepAgents setup.
- [ ] Run `backend/.venv/bin/pytest backend/tests/test_skills_loader.py backend/tests/test_agent_skills.py`.

### Task 3: Verification

**Files:**
- Modify: `openspec/changes/refactor-backend-stream-naming/tasks.md`

- [ ] Run `backend/.venv/bin/pytest backend/tests`.
- [ ] Run `npm run build` from `frontend`.
- [ ] Mark OpenSpec tasks complete.
