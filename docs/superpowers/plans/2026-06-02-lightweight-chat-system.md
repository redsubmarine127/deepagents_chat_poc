# Lightweight Chat System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first usable Vue + Python intelligent chat system with DeepAgents orchestration, OpenAI-compatible model configuration, in-memory conversations, and streaming assistant output.

**Architecture:** The backend is a FastAPI app split into configuration, storage, chat orchestration, SSE encoding, and API routers. The frontend is a Vue 3 + Vite app split into a chat API client and focused chat components. OpenSpec already records the requirements and this implementation must keep those specs aligned.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic Settings, DeepAgents, LangChain OpenAI, pytest, Vue 3, Vite, JavaScript, CSS.

---

## File Structure

Backend files:

- Create `backend/pyproject.toml`: Python package metadata and dependencies.
- Create `backend/.env.example`: local model configuration template without secrets.
- Create `backend/README.md`: run and test instructions.
- Create `backend/app/__init__.py`: app package marker.
- Create `backend/app/main.py`: FastAPI application factory and router wiring.
- Create `backend/app/config.py`: settings model loaded from environment.
- Create `backend/app/api/__init__.py`: API package marker.
- Create `backend/app/api/health.py`: health endpoint.
- Create `backend/app/api/conversations.py`: conversation and stream routes.
- Create `backend/app/chat/__init__.py`: chat package marker.
- Create `backend/app/chat/agent.py`: DeepAgents agent factory and streaming adapter.
- Create `backend/app/chat/schemas.py`: dataclasses and Pydantic request/response models.
- Create `backend/app/chat/service.py`: chat application service.
- Create `backend/app/chat/sse.py`: SSE event formatter.
- Create `backend/app/storage/__init__.py`: storage package marker.
- Create `backend/app/storage/conversations.py`: repository protocol and in-memory implementation.
- Create `backend/tests/test_config.py`: configuration tests.
- Create `backend/tests/test_storage.py`: repository tests.
- Create `backend/tests/test_sse.py`: SSE formatting tests.
- Create `backend/tests/test_chat_service.py`: stream service tests with fake agent.

Frontend files:

- Create `frontend/package.json`: Vite project scripts and dependencies.
- Create `frontend/index.html`: app HTML shell.
- Create `frontend/vite.config.js`: Vite configuration.
- Create `frontend/src/main.js`: Vue mount entry.
- Create `frontend/src/App.vue`: root component.
- Create `frontend/src/api/chat.js`: API client and streaming reader.
- Create `frontend/src/components/ChatShell.vue`: chat state and layout.
- Create `frontend/src/components/MessageList.vue`: message rendering.
- Create `frontend/src/components/MessageInput.vue`: input composer.
- Create `frontend/src/styles.css`: application styling.

Repository files:

- Create `.gitignore`: ignore virtualenvs, node modules, caches, local env files, and build output.

---

## Task 1: Backend Project Skeleton And Configuration

**Files:**

- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/README.md`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/test_config.py`
- Create: `.gitignore`

- [ ] **Step 1: Write failing configuration tests**

Create `backend/tests/test_config.py`:

```python
from app.config import Settings


def test_settings_reads_model_environment(monkeypatch):
    monkeypatch.setenv("MODEL_ID", "test-model")
    monkeypatch.setenv("MODEL_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.2")

    settings = Settings()

    assert settings.model_id == "test-model"
    assert settings.model_base_url == "https://example.test/v1"
    assert settings.model_api_key == "test-key"
    assert settings.model_temperature == 0.2
    assert settings.cors_origins == ["http://127.0.0.1:5173"]


def test_settings_parses_comma_separated_cors(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test,http://b.test")

    settings = Settings()

    assert settings.cors_origins == ["http://a.test", "http://b.test"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend
python -m pytest tests/test_config.py -v
```

Expected: FAIL because `app.config` does not exist.

- [ ] **Step 3: Implement backend metadata and settings**

Create `backend/pyproject.toml`:

```toml
[project]
name = "deepagents-chat-backend"
version = "0.1.0"
description = "Lightweight FastAPI backend for a DeepAgents chat system"
requires-python = ">=3.11"
dependencies = [
  "deepagents>=1.0.0",
  "fastapi>=0.115.0",
  "langchain-openai>=0.3.0",
  "pydantic-settings>=2.6.0",
  "uvicorn[standard]>=0.32.0"
]

[project.optional-dependencies]
dev = [
  "httpx>=0.27.0",
  "pytest>=8.3.0",
  "pytest-asyncio>=0.24.0"
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
pythonpath = ["."]
testpaths = ["tests"]
```

Create `backend/app/config.py`:

```python
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DeepAgents Chat"
    model_id: str = Field(default="gpt-4o-mini", alias="MODEL_ID")
    model_base_url: str = Field(default="https://api.openai.com/v1", alias="MODEL_BASE_URL")
    model_api_key: str | None = Field(default=None, alias="MODEL_API_KEY")
    model_temperature: float = Field(default=0.7, alias="MODEL_TEMPERATURE")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://127.0.0.1:5173"], alias="CORS_ORIGINS")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Create package markers:

```bash
touch backend/app/__init__.py
```

Create `.gitignore`:

```gitignore
.DS_Store
.env
.venv/
__pycache__/
.pytest_cache/
node_modules/
dist/
```

Create `backend/.env.example`:

```dotenv
MODEL_ID=gpt-4o-mini
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_API_KEY=
MODEL_TEMPERATURE=0.7
CORS_ORIGINS=http://127.0.0.1:5173
```

Create `backend/README.md`:

```markdown
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
cd backend
python -m pytest tests/test_config.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .gitignore backend
git commit -m "feat: add backend configuration skeleton"
```

---

## Task 2: Conversation Storage And SSE Encoding

**Files:**

- Create: `backend/app/chat/schemas.py`
- Create: `backend/app/chat/sse.py`
- Create: `backend/app/storage/__init__.py`
- Create: `backend/app/storage/conversations.py`
- Create: `backend/tests/test_storage.py`
- Create: `backend/tests/test_sse.py`

- [ ] **Step 1: Write failing storage and SSE tests**

Create `backend/tests/test_storage.py`:

```python
import pytest

from app.chat.schemas import MessageRole, MessageStatus
from app.storage.conversations import InMemoryConversationRepository, UnknownConversationError


def test_create_conversation_and_append_messages():
    repository = InMemoryConversationRepository()

    conversation = repository.create_conversation()
    message = repository.append_message(conversation.id, role=MessageRole.USER, content="hello")

    assert conversation.id
    assert message.role == MessageRole.USER
    assert message.status == MessageStatus.COMPLETED
    assert repository.get_messages(conversation.id)[0].content == "hello"


def test_unknown_conversation_raises():
    repository = InMemoryConversationRepository()

    with pytest.raises(UnknownConversationError):
        repository.get_messages("missing")
```

Create `backend/tests/test_sse.py`:

```python
import json

from app.chat.sse import format_sse


def test_format_sse_returns_json_data_line():
    payload = format_sse({"type": "delta", "messageId": "m1", "content": "hello"})

    assert payload.startswith("data: ")
    assert payload.endswith("\n\n")
    decoded = json.loads(payload.removeprefix("data: ").strip())
    assert decoded == {"type": "delta", "messageId": "m1", "content": "hello"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend
python -m pytest tests/test_storage.py tests/test_sse.py -v
```

Expected: FAIL because storage and SSE modules do not exist.

- [ ] **Step 3: Implement schemas, repository, and SSE formatter**

Create `backend/app/chat/schemas.py`:

```python
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


def now_utc() -> datetime:
    return datetime.now(UTC)


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageStatus(StrEnum):
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "New conversation"
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str
    role: MessageRole
    content: str
    status: MessageStatus = MessageStatus.COMPLETED
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class CreateConversationResponse(BaseModel):
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime


class MessageResponse(BaseModel):
    id: str
    conversationId: str
    role: MessageRole
    content: str
    status: MessageStatus
    createdAt: datetime
    updatedAt: datetime


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)


def conversation_response(conversation: Conversation) -> CreateConversationResponse:
    return CreateConversationResponse(
        id=conversation.id,
        title=conversation.title,
        createdAt=conversation.created_at,
        updatedAt=conversation.updated_at,
    )


def message_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversationId=message.conversation_id,
        role=message.role,
        content=message.content,
        status=message.status,
        createdAt=message.created_at,
        updatedAt=message.updated_at,
    )
```

Create `backend/app/storage/conversations.py`:

```python
from threading import RLock

from app.chat.schemas import Conversation, Message, MessageRole, MessageStatus, now_utc


class UnknownConversationError(Exception):
    pass


class InMemoryConversationRepository:
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[Message]] = {}
        self._lock = RLock()

    def list_conversations(self) -> list[Conversation]:
        with self._lock:
            return sorted(self._conversations.values(), key=lambda item: item.updated_at, reverse=True)

    def create_conversation(self) -> Conversation:
        with self._lock:
            conversation = Conversation()
            self._conversations[conversation.id] = conversation
            self._messages[conversation.id] = []
            return conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            if conversation is None:
                raise UnknownConversationError(conversation_id)
            return conversation

    def get_messages(self, conversation_id: str) -> list[Message]:
        with self._lock:
            self.get_conversation(conversation_id)
            return list(self._messages[conversation_id])

    def append_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> Message:
        with self._lock:
            conversation = self.get_conversation(conversation_id)
            message = Message(conversation_id=conversation_id, role=role, content=content, status=status)
            self._messages[conversation_id].append(message)
            conversation.updated_at = now_utc()
            return message

    def update_message(
        self,
        conversation_id: str,
        message_id: str,
        *,
        content: str | None = None,
        status: MessageStatus | None = None,
    ) -> Message:
        with self._lock:
            self.get_conversation(conversation_id)
            for message in self._messages[conversation_id]:
                if message.id == message_id:
                    if content is not None:
                        message.content = content
                    if status is not None:
                        message.status = status
                    message.updated_at = now_utc()
                    return message
            raise KeyError(message_id)
```

Create `backend/app/chat/sse.py`:

```python
import json
from typing import Any


def format_sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
```

Create package markers:

```bash
touch backend/app/chat/__init__.py backend/app/storage/__init__.py
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
cd backend
python -m pytest tests/test_storage.py tests/test_sse.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/chat backend/app/storage backend/tests
git commit -m "feat: add conversation storage and sse encoding"
```

---

## Task 3: DeepAgents Adapter And Chat Service

**Files:**

- Create: `backend/app/chat/agent.py`
- Create: `backend/app/chat/service.py`
- Create: `backend/tests/test_chat_service.py`

- [ ] **Step 1: Write failing chat service test**

Create `backend/tests/test_chat_service.py`:

```python
from app.chat.schemas import MessageStatus
from app.chat.service import ChatService
from app.storage.conversations import InMemoryConversationRepository


class FakeAgentRunner:
    async def stream(self, messages):
        assert messages[-1]["role"] == "user"
        yield "hello"
        yield " world"


async def test_chat_service_streams_and_persists_assistant_message():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = ChatService(repository=repository, agent_runner=FakeAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "delta", "delta", "completed"]
    messages = repository.get_messages(conversation.id)
    assert messages[0].content == "hi"
    assert messages[1].content == "hello world"
    assert messages[1].status == MessageStatus.COMPLETED
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend
python -m pytest tests/test_chat_service.py -v
```

Expected: FAIL because `ChatService` does not exist.

- [ ] **Step 3: Implement DeepAgents adapter and chat service**

Create `backend/app/chat/agent.py`:

```python
from collections.abc import AsyncIterator

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

from app.config import Settings

SYSTEM_PROMPT = (
    "You are a helpful intelligent conversation assistant. "
    "Answer clearly and concisely. Use Chinese when the user writes Chinese, "
    "and English when the user writes English."
)


class DeepAgentRunner:
    def __init__(self, settings: Settings) -> None:
        if not settings.model_api_key:
            raise ValueError("MODEL_API_KEY is required for remote model streaming.")
        model = ChatOpenAI(
            model=settings.model_id,
            base_url=settings.model_base_url,
            api_key=settings.model_api_key,
            temperature=settings.model_temperature,
            streaming=True,
        )
        self._agent = create_deep_agent(model=model, tools=[], system_prompt=SYSTEM_PROMPT)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        async for event in self._agent.astream_events({"messages": messages}, version="v2"):
            event_type = event.get("event")
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                content = getattr(chunk, "content", "")
                if isinstance(content, str) and content:
                    yield content
```

Create `backend/app/chat/service.py`:

```python
from collections.abc import AsyncIterator
from typing import Protocol

from app.chat.schemas import MessageRole, MessageStatus
from app.storage.conversations import InMemoryConversationRepository


class AgentRunner(Protocol):
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        ...


class ChatService:
    def __init__(self, repository: InMemoryConversationRepository, agent_runner: AgentRunner) -> None:
        self._repository = repository
        self._agent_runner = agent_runner

    async def stream_user_message(self, conversation_id: str, content: str) -> AsyncIterator[dict[str, str]]:
        text = content.strip()
        if not text:
            raise ValueError("Message content is required.")

        self._repository.append_message(conversation_id, role=MessageRole.USER, content=text)
        assistant = self._repository.append_message(
            conversation_id,
            role=MessageRole.ASSISTANT,
            content="",
            status=MessageStatus.STREAMING,
        )
        yield {"type": "started", "messageId": assistant.id, "content": ""}

        chunks: list[str] = []
        history = [
            {"role": message.role.value, "content": message.content}
            for message in self._repository.get_messages(conversation_id)
            if message.id != assistant.id
        ]
        try:
            async for chunk in self._agent_runner.stream(history):
                chunks.append(chunk)
                yield {"type": "delta", "messageId": assistant.id, "content": chunk}
            final_content = "".join(chunks)
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=final_content,
                status=MessageStatus.COMPLETED,
            )
            yield {"type": "completed", "messageId": assistant.id, "content": final_content}
        except Exception as exc:
            failure = f"Assistant generation failed: {exc}"
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=failure,
                status=MessageStatus.FAILED,
            )
            yield {"type": "failed", "messageId": assistant.id, "content": failure}
```

- [ ] **Step 4: Run service test to verify it passes**

Run:

```bash
cd backend
python -m pytest tests/test_chat_service.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/chat/agent.py backend/app/chat/service.py backend/tests/test_chat_service.py
git commit -m "feat: add deepagents chat service"
```

---

## Task 4: FastAPI Routes

**Files:**

- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/health.py`
- Create: `backend/app/api/conversations.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: Write failing API tests**

Create `backend/tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_conversation_messages():
    client = TestClient(app)

    created = client.post("/api/conversations")
    conversation_id = created.json()["id"]

    conversations = client.get("/api/conversations")
    messages = client.get(f"/api/conversations/{conversation_id}/messages")

    assert created.status_code == 200
    assert conversations.status_code == 200
    assert conversations.json()[0]["id"] == conversation_id
    assert messages.status_code == 200
    assert messages.json() == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend
python -m pytest tests/test_api.py -v
```

Expected: FAIL because `app.main` does not exist.

- [ ] **Step 3: Implement API routes and app wiring**

Create `backend/app/api/health.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Create `backend/app/api/conversations.py`:

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.chat.schemas import SendMessageRequest, conversation_response, message_response
from app.chat.sse import format_sse
from app.chat.service import ChatService
from app.storage.conversations import InMemoryConversationRepository, UnknownConversationError


def create_router(repository: InMemoryConversationRepository, chat_service: ChatService) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/conversations")
    def list_conversations():
        return [conversation_response(item) for item in repository.list_conversations()]

    @router.post("/conversations")
    def create_conversation():
        return conversation_response(repository.create_conversation())

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(conversation_id: str):
        try:
            return [message_response(item) for item in repository.get_messages(conversation_id)]
        except UnknownConversationError as exc:
            raise HTTPException(status_code=404, detail="Conversation not found.") from exc

    @router.post("/conversations/{conversation_id}/messages/stream")
    async def stream_message(conversation_id: str, request: SendMessageRequest):
        async def event_stream():
            try:
                async for event in chat_service.stream_user_message(conversation_id, request.content):
                    yield format_sse(event)
            except UnknownConversationError:
                yield format_sse({"type": "failed", "messageId": "", "content": "Conversation not found."})
            except ValueError as exc:
                yield format_sse({"type": "failed", "messageId": "", "content": str(exc)})

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return router
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.conversations import create_router as create_conversations_router
from app.api.health import router as health_router
from app.chat.agent import DeepAgentRunner
from app.chat.service import ChatService
from app.config import get_settings
from app.storage.conversations import InMemoryConversationRepository

settings = get_settings()
repository = InMemoryConversationRepository()
agent_runner = DeepAgentRunner(settings)
chat_service = ChatService(repository=repository, agent_runner=agent_runner)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(create_conversations_router(repository, chat_service))
```

Create package marker:

```bash
touch backend/app/api/__init__.py
```

- [ ] **Step 4: Run API tests and fix startup testability if needed**

Run:

```bash
cd backend
python -m pytest tests/test_api.py -v
```

Expected: PASS. If `MODEL_API_KEY` absence breaks app import, refactor `DeepAgentRunner` construction behind lazy initialization in `ChatService` or provide a test fake app factory.

- [ ] **Step 5: Commit**

```bash
git add backend/app/api backend/app/main.py backend/tests/test_api.py
git commit -m "feat: add fastapi chat routes"
```

---

## Task 5: Vue Frontend Chat Experience

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/api/chat.js`
- Create: `frontend/src/components/ChatShell.vue`
- Create: `frontend/src/components/MessageList.vue`
- Create: `frontend/src/components/MessageInput.vue`
- Create: `frontend/src/styles.css`

- [ ] **Step 1: Create frontend package and app shell**

Create `frontend/package.json`:

```json
{
  "name": "deepagents-chat-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "vite": "^6.0.0",
    "vue": "^3.5.0"
  },
  "devDependencies": {}
}
```

Create `frontend/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DeepAgents Chat</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

Create `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5173
  }
})
```

Create `frontend/src/main.js`:

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import './styles.css'

createApp(App).mount('#app')
```

Create `frontend/src/App.vue`:

```vue
<template>
  <ChatShell />
</template>

<script setup>
import ChatShell from './components/ChatShell.vue'
</script>
```

- [ ] **Step 2: Implement chat API client**

Create `frontend/src/api/chat.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8090'

export async function createConversation() {
  const response = await fetch(`${API_BASE_URL}/api/conversations`, { method: 'POST' })
  if (!response.ok) throw new Error('Unable to create conversation')
  return response.json()
}

export async function listMessages(conversationId) {
  const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages`)
  if (!response.ok) throw new Error('Unable to load messages')
  return response.json()
}

export async function streamMessage(conversationId, content, onEvent) {
  const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}/messages/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  })
  if (!response.ok || !response.body) throw new Error('Unable to start message stream')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split('\n\n')
    buffer = frames.pop() || ''
    for (const frame of frames) {
      const line = frame.split('\n').find((item) => item.startsWith('data: '))
      if (line) onEvent(JSON.parse(line.slice(6)))
    }
  }
}
```

- [ ] **Step 3: Implement Vue chat components**

Create `frontend/src/components/MessageInput.vue`:

```vue
<template>
  <form class="composer" @submit.prevent="submit">
    <textarea
      v-model="draft"
      :disabled="disabled"
      rows="2"
      placeholder="输入消息..."
      @keydown.enter.exact.prevent="submit"
    />
    <button type="submit" :disabled="disabled || !draft.trim()">Send</button>
  </form>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['send'])
const draft = ref('')

function submit() {
  const content = draft.value.trim()
  if (!content) return
  emit('send', content)
  draft.value = ''
}
</script>
```

Create `frontend/src/components/MessageList.vue`:

```vue
<template>
  <div class="messages">
    <div v-if="messages.length === 0" class="empty-state">开始一段对话</div>
    <article
      v-for="message in messages"
      :key="message.id"
      class="message"
      :class="[`message-${message.role}`, { failed: message.status === 'failed' }]"
    >
      <div class="message-role">{{ message.role === 'user' ? 'You' : 'Assistant' }}</div>
      <div class="message-content">{{ message.content }}</div>
    </article>
  </div>
</template>

<script setup>
defineProps({
  messages: { type: Array, required: true }
})
</script>
```

Create `frontend/src/components/ChatShell.vue`:

```vue
<template>
  <main class="chat-shell">
    <header class="topbar">
      <div>
        <h1>DeepAgents Chat</h1>
        <p>Lightweight streaming conversation</p>
      </div>
      <button type="button" class="icon-button" title="New conversation" @click="startConversation">+</button>
    </header>

    <MessageList :messages="messages" />
    <MessageInput :disabled="isStreaming || !conversationId" @send="send" />
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createConversation, listMessages, streamMessage } from '../api/chat'
import MessageInput from './MessageInput.vue'
import MessageList from './MessageList.vue'

const conversationId = ref('')
const messages = ref([])
const isStreaming = ref(false)

async function startConversation() {
  const conversation = await createConversation()
  conversationId.value = conversation.id
  messages.value = await listMessages(conversation.id)
}

async function send(content) {
  if (!conversationId.value || isStreaming.value) return

  const localUserMessage = {
    id: crypto.randomUUID(),
    conversationId: conversationId.value,
    role: 'user',
    content,
    status: 'completed'
  }
  messages.value.push(localUserMessage)
  isStreaming.value = true

  try {
    await streamMessage(conversationId.value, content, (event) => {
      if (event.type === 'started') {
        messages.value.push({
          id: event.messageId,
          conversationId: conversationId.value,
          role: 'assistant',
          content: '',
          status: 'streaming'
        })
      }
      const assistant = messages.value.find((message) => message.id === event.messageId)
      if (!assistant) return
      if (event.type === 'delta') assistant.content += event.content
      if (event.type === 'completed') {
        assistant.content = event.content || assistant.content
        assistant.status = 'completed'
      }
      if (event.type === 'failed') {
        assistant.content = event.content
        assistant.status = 'failed'
      }
    })
  } catch (error) {
    messages.value.push({
      id: crypto.randomUUID(),
      conversationId: conversationId.value,
      role: 'assistant',
      content: error.message,
      status: 'failed'
    })
  } finally {
    isStreaming.value = false
  }
}

onMounted(startConversation)
</script>
```

- [ ] **Step 4: Add responsive styling**

Create `frontend/src/styles.css`:

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: #f5f7f8;
  color: #182026;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

button,
textarea {
  font: inherit;
}

.chat-shell {
  display: grid;
  grid-template-rows: auto 1fr auto;
  width: min(920px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  background: #ffffff;
  border-left: 1px solid #dde3e6;
  border-right: 1px solid #dde3e6;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid #dde3e6;
}

.topbar h1 {
  margin: 0;
  font-size: 20px;
}

.topbar p {
  margin: 4px 0 0;
  color: #66737a;
  font-size: 13px;
}

.icon-button {
  width: 36px;
  height: 36px;
  border: 1px solid #c9d2d7;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  margin: auto;
  color: #66737a;
}

.message {
  max-width: min(720px, 92%);
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #dde3e6;
  background: #ffffff;
}

.message-user {
  align-self: flex-end;
  background: #e9f3ff;
  border-color: #b9d6f2;
}

.message-assistant {
  align-self: flex-start;
  background: #f8faf6;
  border-color: #d8e3cf;
}

.message.failed {
  background: #fff1f1;
  border-color: #efb3b3;
}

.message-role {
  margin-bottom: 6px;
  color: #66737a;
  font-size: 12px;
  font-weight: 700;
}

.message-content {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  line-height: 1.55;
}

.composer {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  padding: 16px 20px 20px;
  border-top: 1px solid #dde3e6;
}

.composer textarea {
  min-height: 48px;
  max-height: 180px;
  resize: vertical;
  border: 1px solid #c9d2d7;
  border-radius: 8px;
  padding: 10px 12px;
}

.composer button {
  min-width: 84px;
  height: 48px;
  border: 0;
  border-radius: 8px;
  background: #1f6f8b;
  color: #ffffff;
  cursor: pointer;
}

.composer button:disabled,
.composer textarea:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

@media (max-width: 640px) {
  .chat-shell {
    border: 0;
  }

  .composer {
    grid-template-columns: 1fr;
  }

  .composer button {
    width: 100%;
  }
}
```

- [ ] **Step 5: Build frontend**

Run:

```bash
cd frontend
npm install
npm run build
```

Expected: PASS and `dist/` is created.

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: add vue streaming chat frontend"
```

---

## Task 6: Final Verification And Documentation Alignment

**Files:**

- Modify: `openspec/changes/initial-chat-system/tasks.md`
- Modify: `backend/README.md` if run instructions changed during implementation.

- [ ] **Step 1: Run backend tests**

Run:

```bash
cd backend
python -m pytest -v
```

Expected: PASS.

- [ ] **Step 2: Run frontend build**

Run:

```bash
cd frontend
npm run build
```

Expected: PASS.

- [ ] **Step 3: Mark OpenSpec implementation tasks complete**

Update `openspec/changes/initial-chat-system/tasks.md` so every implemented task is checked:

```markdown
- [x] Create Python backend project structure.
- [x] Add configuration loading for OpenAI-compatible model settings.
- [x] Implement in-memory conversation repository.
- [x] Implement DeepAgents chat agent factory.
- [x] Implement chat service and SSE event encoding.
- [x] Add FastAPI routes for health, conversations, messages, and streaming.
- [x] Add backend tests for configuration, repository behavior, and SSE formatting.
- [x] Create Vue frontend project structure.
- [x] Implement chat API client and stream reader.
- [x] Implement chat shell, message list, and input components.
- [x] Add frontend build validation.
- [x] Run backend and frontend smoke checks.
```

- [ ] **Step 4: Inspect git status**

Run:

```bash
git status --short
```

Expected: only intended files are modified.

- [ ] **Step 5: Commit final verification updates**

```bash
git add openspec backend/README.md
git commit -m "docs: mark initial chat implementation complete"
```

---

## Self-Review Notes

- Spec coverage: The plan covers DeepAgents backend orchestration, OpenAI-compatible configuration, streaming, Vue frontend, in-memory repository, and OpenSpec task tracking.
- Placeholder scan: No task uses placeholder requirements; each task has concrete files and commands.
- Type consistency: The plan consistently uses `conversation_id` in backend routes and `conversationId` in frontend-facing JSON fields.
