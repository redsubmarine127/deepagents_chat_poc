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
HUMAN_LOOP_ENABLED=false
```

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
```

## Test

```bash
python -m pytest -v
```

## Runtime

`app.main:create_app()` builds the FastAPI app through `app.runtime.build_runtime()`. Runtime assembly creates:

- An in-memory conversation repository.
- An in-memory approval store.
- A single tool catalog scan for metadata and executable tools.
- Tool metadata records include `available` and `loadError` so bad tools are visible but not treated as executable.
- A DeepAgents runner. `interrupt_on` for `write_file` and `edit_file` is only configured when `HUMAN_LOOP_ENABLED=true`.
- An in-memory LangGraph checkpointer for approval resume during the current process lifetime.

Approval resume endpoints stream SSE responses:

- `POST /api/human-loop/approvals/{approval_id}/approve/stream`
- `POST /api/human-loop/approvals/{approval_id}/reject/stream`

## Logs

Operational logs are written through Python `logging` and appear in the uvicorn terminal. Logs include chat lifecycle events, model stream chunks, tool calls, skill loading, tool catalog loading, approval creation, and approval resume. Long content is summarized, and sensitive payload keys are redacted.
