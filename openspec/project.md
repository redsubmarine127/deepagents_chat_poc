# Project Specification

## Mission

Build a simple, lightweight intelligent conversation system that provides a Vue chat interface, a Python backend, DeepAgents-based response orchestration, configurable OpenAI-compatible models, and streaming assistant output.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `backend/` | Python 3.11+ FastAPI backend using DeepAgents |
| `frontend/` | Vue 3 + Vite chat frontend |
| `openspec/` | Durable product and engineering specifications |
| `docs/superpowers/` | Design and implementation planning documents |

## Runtime Topology

| Service | Default Port | Notes |
| --- | ---: | --- |
| Python backend | `8090` | FastAPI API and streaming endpoint |
| Vue frontend | `5173` | Vite development server |

## Global Requirements

- The backend MUST use the DeepAgents framework for the conversation orchestration path.
- The frontend MUST use Vue.
- The backend MUST support OpenAI-compatible model providers.
- The model ID and API base URL MUST be configurable without code changes.
- The chat endpoint MUST stream assistant output.
- Version 1 MUST focus on basic conversation only.
- Version 1 MUST use in-memory conversation storage behind a repository interface.
- Secrets MUST be provided through environment variables or local configuration and MUST NOT be committed.
- Every requirement adjustment MUST be recorded in OpenSpec under `openspec/changes/`.

## Shared API Contract

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/conversations` | List conversations |
| `POST` | `/api/conversations` | Create conversation |
| `GET` | `/api/conversations/{conversation_id}/messages` | List messages |
| `POST` | `/api/conversations/{conversation_id}/messages/stream` | Send a message and stream assistant output |

## SSE Event Contract

Streaming responses MUST use `text/event-stream` and emit JSON payloads shaped like:

```json
{
  "type": "started | delta | completed | failed",
  "messageId": "uuid",
  "content": "string"
}
```

Expected event flow:

1. `started`
2. zero or more `delta`
3. exactly one terminal event: `completed` or `failed`
