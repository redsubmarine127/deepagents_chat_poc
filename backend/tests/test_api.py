from fastapi.testclient import TestClient

from fastapi import FastAPI

from app.api.conversations import create_router as create_conversations_router
from app.main import app
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository


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


def test_list_skills_endpoint_returns_metadata():
    client = TestClient(app)

    response = client.get("/api/skills")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_tools_endpoint_returns_metadata():
    client = TestClient(app)

    response = client.get("/api/tools")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_human_loop_approval_endpoints():
    client = TestClient(app)

    created = client.post(
        "/api/human-loop/approvals",
        json={"toolName": "write_file", "description": "Write file", "payload": {"path": "/tmp/a.txt"}},
    )
    approval_id = created.json()["id"]
    listed = client.get("/api/human-loop/approvals")
    approved = client.post(f"/api/human-loop/approvals/{approval_id}/approve")

    assert created.status_code == 200
    assert listed.status_code == 200
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_stream_without_api_key_returns_failed_event():
    client = TestClient(app)
    conversation_id = client.post("/api/conversations").json()["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages/stream",
        json={"content": "hello"},
    )

    assert response.status_code == 200
    assert "data: " in response.text
    assert '"type": "started"' in response.text
    assert '"type": "failed"' in response.text


def test_stream_busy_conversation_returns_conflict():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()

    class BusyChatService:
        def stream_user_message(self, conversation_id, content):
            raise ConversationBusyError(conversation_id)

    test_app = FastAPI()
    test_app.include_router(create_conversations_router(repository, BusyChatService()))
    client = TestClient(test_app)

    response = client.post(f"/conversations/{conversation.id}/messages/stream", json={"content": "hello"})

    assert response.status_code == 409
