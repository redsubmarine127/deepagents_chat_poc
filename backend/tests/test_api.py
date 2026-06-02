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
