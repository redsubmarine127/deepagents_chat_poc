# On-Demand Skill Loading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add local skill discovery and DeepAgents on-demand skill loading to the chat system.

**Architecture:** Backend discovers skill metadata from `skills/`, exposes it via `GET /api/skills`, and passes the skill source to DeepAgents only when enabled and available. Frontend reads `/api/skills` and shows a compact skill count/list in the chat header.

**Tech Stack:** Python 3.12, FastAPI, DeepAgents SkillsMiddleware, pytest, Vue 3, Vite.

---

## Tasks

- [ ] Add backend settings for `SKILLS_ENABLED` and `SKILLS_DIR`.
- [ ] Add `app.skills.loader` and tests for metadata discovery.
- [ ] Add `/api/skills` route and API tests.
- [ ] Update `DeepAgentRunner` to pass DeepAgents `skills` and filesystem backend.
- [ ] Update frontend API client and chat header skill display.
- [ ] Run backend tests, frontend build, and browser smoke check.
