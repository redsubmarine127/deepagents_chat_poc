# System Prompt Loading Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Load the DeepAgents base system prompt from a configured local file.

**Architecture:** Add `app.chat.prompts` as a focused loader module. `DeepAgentRunner` resolves the repository root, loads the prompt file through the loader, and passes the result to `create_deep_agent`.

**Tech Stack:** Python 3.12, FastAPI, DeepAgents, pytest.

---

## Tasks

- [ ] Add `SYSTEM_PROMPT_PATH` setting.
- [ ] Add prompt loader tests and implementation.
- [ ] Wire `DeepAgentRunner` to use the loaded prompt.
- [ ] Add default `prompts/system.md`.
- [ ] Update `.env.example` and OpenSpec tasks.
- [ ] Run backend tests and frontend build.
