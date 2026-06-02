# Initial Chat System Proposal

## Summary

Create the first version of a lightweight intelligent chat system with a Vue frontend, Python backend, DeepAgents orchestration, OpenAI-compatible model configuration, and streaming assistant responses.

## Motivation

The project needs a small but extensible base that proves the core conversation loop before adding durable storage, RAG, tools, authentication, or advanced agent workflows.

## Scope

In scope:

- Vue 3 chat frontend.
- Python FastAPI backend.
- DeepAgents-based conversation orchestration.
- OpenAI-compatible model configuration through environment variables.
- SSE streaming response output.
- In-memory conversation storage behind a repository interface.
- OpenSpec records for requirement tracking.

Out of scope:

- User login.
- Durable database storage.
- File upload.
- RAG.
- MCP tools.
- Admin dashboards.
- Multi-agent task UI.

## Decisions

- Use in-memory storage for version 1 and keep the repository boundary ready for future persistence.
- Use `text/event-stream` for browser-friendly streaming.
- Keep the frontend as a direct chat experience, with no landing page.
- Record this and future requirement changes under `openspec/changes/`.
