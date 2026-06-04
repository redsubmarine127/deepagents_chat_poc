# Agent Reasoning Trace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stream observable agent execution events and TodoList updates to the UI while logging TodoList changes in the backend.

**Architecture:** `DeepAgentRunner` maps DeepAgents event stream callbacks into structured `reasoning` and `delta` events. `ChatService` forwards reasoning events over SSE and persists only assistant answer text. Vue stores reasoning entries on the assistant message and renders them in a compact collapsible panel.

**Tech Stack:** Python 3.12, DeepAgents event stream, FastAPI SSE, pytest, Vue 3, Vite.

---

## Tasks

- [ ] Add structured agent stream event tests.
- [ ] Convert DeepAgents tool events to reasoning SSE events.
- [ ] Log `write_todos` updates in the backend.
- [ ] Update ChatService to persist only `delta` content.
- [ ] Update Vue to render reasoning events.
- [ ] Run backend tests, frontend build, and browser smoke check.
