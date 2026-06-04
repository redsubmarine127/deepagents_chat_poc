# API Router Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `backend/app/api` into clearer router aggregation and error helper modules without changing public API behavior.

**Architecture:** Child route modules define only their local paths. `api/router.py` owns the shared `/api` prefix and includes child routers. `api/errors.py` owns repeated HTTP and SSE failure conversion.

**Tech Stack:** Python, FastAPI, pytest.

---

### Task 1: Add API Modules

**Files:**
- Create: `backend/app/api/router.py`
- Create: `backend/app/api/errors.py`
- Modify: `backend/app/api/conversations.py`
- Modify: `backend/app/api/skills.py`
- Modify: `backend/app/api/health.py`
- Modify: `backend/app/main.py`

- [ ] Add route aggregation in `router.py`.
- [ ] Add error helpers in `errors.py`.
- [ ] Remove repeated `/api` prefixes from child routers.
- [ ] Include only the aggregate router from `main.py`.

### Task 2: Verify Compatibility

**Files:**
- Modify: `openspec/changes/refactor-api-router-structure/tasks.md`

- [ ] Run `backend/.venv/bin/pytest backend/tests/test_api.py`.
- [ ] Run `backend/.venv/bin/pytest backend/tests`.
- [ ] Run `npm run build` from `frontend`.
- [ ] Mark OpenSpec tasks complete.
