# Lightweight Intelligent Chat System Design

## Goal

Build a simple, lightweight intelligent chat system. Version 1 supports only conversation: a Vue frontend sends user messages to a Python backend, the backend uses the DeepAgents framework to orchestrate responses, and assistant output streams back to the browser.

## Scope

Version 1 includes:

- Basic conversation creation and message listing.
- User-to-assistant chat with streaming output.
- A Python backend built with FastAPI and DeepAgents.
- A Vue 3 frontend built with Vite.
- OpenAI-compatible model configuration through environment variables.
- In-memory conversation storage through a repository interface that can later be replaced by durable storage.
- OpenSpec records for the initial requirements and future requirement changes.

Version 1 excludes:

- Authentication and user accounts.
- File upload.
- RAG.
- MCP tools.
- Multi-agent task panels.
- Durable database storage.
- Billing, analytics, or admin workflows.

## Architecture

The repository is split into three main areas:

| Path | Purpose |
| --- | --- |
| `backend/` | Python 3.11+ FastAPI service using DeepAgents for chat orchestration |
| `frontend/` | Vue 3 + Vite single-page chat UI |
| `openspec/` | Durable product and engineering specifications plus change records |

Runtime topology:

| Service | Default URL | Notes |
| --- | --- | --- |
| Backend | `http://127.0.0.1:8090` | FastAPI API and SSE stream endpoint |
| Frontend | `http://127.0.0.1:5173` | Vite development server |

## Backend Design

The backend exposes a small HTTP API:

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/conversations` | List conversations |
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations/{conversation_id}/messages` | List messages for a conversation |
| `POST` | `/api/conversations/{conversation_id}/messages/stream` | Append a user message and stream the assistant response |

The backend uses these internal units:

| Unit | Responsibility |
| --- | --- |
| `config` | Read model, CORS, and runtime settings from environment variables |
| `storage` | Provide `ConversationRepository` and an in-memory implementation |
| `chat.agent` | Build the DeepAgents agent using a configurable OpenAI-compatible model |
| `chat.service` | Coordinate persistence, agent execution, and streamed assistant messages |
| `chat.sse` | Encode JSON events as `text/event-stream` chunks |
| `api` | FastAPI routers and request/response schemas |

## DeepAgents Integration

The backend creates a DeepAgents graph through `create_deep_agent(...)`. Version 1 does not add custom tools. It uses a focused system prompt that frames the agent as a helpful Chinese/English conversational assistant and keeps behavior suitable for short chat sessions.

The agent receives the conversation history as messages. The stream endpoint converts DeepAgents stream updates into the client-facing SSE contract. If DeepAgents or the remote model fails, the backend emits one `failed` event and records the assistant message as failed when possible.

## Model Configuration

The model MUST use an OpenAI-compatible format and be configurable without code changes.

Environment variables:

| Variable | Purpose | Example |
| --- | --- | --- |
| `MODEL_ID` | OpenAI-compatible model identifier | `gpt-4o-mini` |
| `MODEL_BASE_URL` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `MODEL_API_KEY` | API key for the configured provider | `sk-...` |
| `MODEL_TEMPERATURE` | Sampling temperature | `0.7` |

The backend SHOULD fail fast at startup or first request with a clear configuration error if required model settings are missing. Secrets MUST NOT be committed.

## Streaming Contract

The stream endpoint returns `text/event-stream`. Each event carries a JSON payload:

```json
{
  "type": "started | delta | completed | failed",
  "messageId": "uuid",
  "content": "string"
}
```

Expected flow:

1. Emit `started` when the assistant message is created.
2. Emit zero or more `delta` events as model text arrives.
3. Emit exactly one terminal event: `completed` or `failed`.

The frontend treats `delta` as append-only text and finalizes the assistant bubble on `completed`.

## Persistence Boundary

Version 1 uses in-memory storage, selected because the first release is a proof of concept and should remain lightweight. Storage is still implemented through a repository interface:

- `list_conversations()`
- `create_conversation()`
- `get_messages(conversation_id)`
- `append_message(conversation_id, message)`
- `update_message(conversation_id, message_id, updates)`

This keeps the API and chat service independent from the storage implementation. Later database storage can be added by implementing the same interface.

## Frontend Design

The frontend is a Vue 3 + Vite single-page app. The first screen is the usable chat experience, not a landing page.

Core components:

| Component | Responsibility |
| --- | --- |
| `ChatShell.vue` | Overall layout, conversation state, send flow |
| `MessageList.vue` | Render user and assistant messages |
| `MessageInput.vue` | Text input, submit button, disabled/loading state |
| `api/chat.js` | Backend API client and stream reader |

The UI supports:

- Creating or loading the default conversation on startup.
- Showing user and assistant messages.
- Sending a user message with Enter or the send button.
- Rendering streaming assistant content incrementally.
- Showing a concise error state when a stream fails.

The UI does not include marketing sections, hero content, file upload controls, or unused agent tooling.

## Error Handling

Backend:

- Invalid conversation IDs return `404`.
- Empty messages return `400`.
- Model configuration errors produce a `failed` SSE event for stream requests.
- Remote model errors are converted into user-readable failures.

Frontend:

- Empty input is not sent.
- During streaming, the input remains usable only after the current response finishes.
- Failed streams keep the user message visible and mark the assistant response as failed.

## OpenSpec Workflow

The repository MUST keep requirements in `openspec/`. Every requirement adjustment MUST create or update a change record under `openspec/changes/<change-id>/`.

For this first version, the initial change is:

```text
openspec/changes/initial-chat-system/
  proposal.md
  tasks.md
  specs/chat/spec.md
```

The durable chat capability spec lives at:

```text
openspec/specs/chat/spec.md
```

## Testing Strategy

Backend tests:

- Configuration loading.
- In-memory conversation repository behavior.
- SSE event formatting.
- Chat service behavior with a fake streaming agent.

Frontend checks:

- `npm run build`.
- Manual browser check that messages stream into the assistant bubble.

End-to-end smoke check:

1. Start backend on `127.0.0.1:8090`.
2. Start frontend on `127.0.0.1:5173`.
3. Send a message.
4. Confirm `started`, `delta`, and `completed` behavior is visible in the UI.

## Approval

The selected approach is the DeepAgents standard orchestration design with in-memory storage and a durable storage interface reserved for future implementations.
