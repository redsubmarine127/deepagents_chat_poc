# DeepAgents Chat Backend

## Setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Set `MODEL_API_KEY`, `MODEL_ID`, and `MODEL_BASE_URL` in `.env`.

## Run

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
```

## Test

```bash
python -m pytest -v
```
