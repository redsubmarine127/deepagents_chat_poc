# DeepAgents Chat Backend

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Set runtime configuration in `.env`:

```env
APP_NAME=DeepAgents Chat
MODEL_ID=gpt-4o-mini
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_API_KEY=
MODEL_TEMPERATURE=0.7
CORS_ORIGINS=http://127.0.0.1:5173,http://127.0.0.1:5174
SKILLS_ENABLED=true
SKILLS_DIR=skills
SYSTEM_PROMPT_PATH=prompts/system.md
TOOLS_ENABLED=true
TOOLS_DIR=tools
AGENT_MAX_RETRIES=3
```

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
```

## Test

```bash
python -m pytest -v
```

## Chat API

Use one endpoint for message submission:

```http
POST /api/conversations/messages
Content-Type: application/json
```

```json
{
  "sessionId": "session-001",
  "streamFlag": "stream",
  "query": "hello",
  "messageId": "turn-001",
  "globalUserId": "user-001",
  "userAccount": "demo-account",
  "payload": {}
}
```

- The frontend generates a default `sessionId` before the first message. Blank values are still accepted and create a new generated conversation ID.
- Unknown non-blank `sessionId` values create a conversation using that ID.
- Existing `sessionId` values continue that conversation.
- `streamFlag=stream` returns SSE with the unified output fields plus `sessionId` and `messageId`.
- `streamFlag=nonStream` returns JSON with the unified output fields plus `sessionId`, `messageId`, and `payload`.
- Unified output fields are `state`, `stateDesc`, `content`, `processResult`, `searchList`, `log`, `endFlag`, and `error`. Fields with no value may be omitted.
- Fields default to strings except `processResult` as JSON, `searchList` as a list, and `endFlag=true` when the conversation turn is finished.
- `state` values are `THINKING` and `GENERATE`. State and state description are emitted as standalone phase-boundary frames, such as before thinking starts and before answer generation starts.
- `THINKING` content frames wrap `content` in `<think>...</think>`.
- `messageId` is the caller-provided turn ID and is echoed in responses. The backend internal assistant message ID is not exposed through the chat message API.
- `POST /api/conversations` is no longer used as a standalone conversation creation endpoint.
- `GET /api/conversations/{conversation_id}/messages` remains available for message history.

## Runtime

`app.main:create_app()` builds the FastAPI app through `app.runtime.build_runtime()`. Runtime assembly creates:

- An in-memory conversation repository.
- A single tool catalog scan for metadata and executable tools.
- Tool metadata records include `available` and `loadError` so bad tools are visible but not treated as executable.
- A DeepAgents runner with local tools and skill loading.

The `dev_zfs` branch does not include human-in-the-loop approval APIs or frontend approval UI.

## Logs

Operational logs are written through Python `logging` and appear in the uvicorn terminal. Logs include chat lifecycle events, model stream chunks, tool calls, skill loading, and tool catalog loading. Long content is summarized, and sensitive payload keys are redacted.
