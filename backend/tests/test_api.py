from fastapi.testclient import TestClient

import json

from fastapi import FastAPI

from app.api.conversations import create_router as create_conversations_router
from app.main import app
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository


def sse_payloads(response):
    payloads = []
    for frame in response.text.split("\n\n"):
        if frame.startswith("data: "):
            payloads.append(json.loads(frame.removeprefix("data: ")))
    return payloads


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_list_conversation_messages():
    client = TestClient(app)
    conversation_id = "api-test-list-session"

    created = client.post(
        "/api/conversations/messages",
        json={
            "sessionId": conversation_id,
            "streamFlag": "nonStream",
            "query": "hello",
            "messageId": "turn-list",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {},
        },
    )

    conversations = client.get("/api/conversations")
    messages = client.get(f"/api/conversations/{conversation_id}/messages")

    assert created.status_code == 200
    assert created.json()["sessionId"] == conversation_id
    assert conversations.status_code == 200
    assert conversations.json()[0]["id"] == conversation_id
    assert messages.status_code == 200
    assert messages.json()[0]["content"] == "hello"


def test_create_conversation_endpoint_is_removed():
    client = TestClient(app)

    response = client.post("/api/conversations")

    assert response.status_code == 405


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


def test_human_loop_approval_endpoints_are_removed():
    client = TestClient(app)

    response = client.get("/api/human-loop/approvals")

    assert response.status_code == 404


def test_stream_without_api_key_returns_failed_event():
    client = TestClient(app)

    response = client.post(
        "/api/conversations/messages",
        json={
            "sessionId": "",
            "streamFlag": "stream",
            "query": "hello",
            "messageId": "turn-1",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {"channel": "test"},
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data: " in response.text
    payloads = sse_payloads(response)
    started = payloads[0]
    failed = payloads[-1]
    assert started["state"] == "THINKING"
    assert started["stateDesc"] == "思考中"
    assert started["log"] == "chat.stream.started"
    assert started["sessionId"]
    assert started["messageId"] == "turn-1"
    assert "content" not in started
    assert "processResult" not in started
    assert "searchList" not in started
    assert "endFlag" not in started
    assert "error" not in started
    assert "assistantMessageId" not in started
    assert "requestMessageId" not in started
    assert "state" not in failed
    assert "stateDesc" not in failed
    assert failed["endFlag"] is True
    assert failed["error"]


def test_stream_reasoning_content_is_wrapped_with_think_tag():
    repository = InMemoryConversationRepository()

    class ReasoningChatService:
        def stream_user_message(self, conversation_id, content):
            async def events():
                yield {"type": "reasoning", "content": "分析问题", "messageId": "assistant-1"}
                yield {"type": "delta", "content": "答案", "messageId": "assistant-1"}
                yield {"type": "completed", "content": "答案", "messageId": "assistant-1"}

            return events()

    test_app = FastAPI()
    test_app.include_router(create_conversations_router(repository, ReasoningChatService()))
    client = TestClient(test_app)

    response = client.post(
        "/conversations/messages",
        json={
            "sessionId": "think-session",
            "streamFlag": "stream",
            "query": "hello",
            "messageId": "turn-think",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {},
        },
    )

    payloads = sse_payloads(response)

    assert payloads == [
        {
            "state": "THINKING",
            "stateDesc": "思考中",
            "log": "chat.thinking.start",
            "sessionId": "think-session",
            "messageId": "turn-think",
        },
        {
            "content": "<think>分析问题</think>",
            "processResult": {"content": "分析问题"},
            "log": "chat.thinking.delta",
            "sessionId": "think-session",
            "messageId": "turn-think",
        },
        {
            "state": "GENERATE",
            "stateDesc": "生成答案",
            "log": "chat.generate.start",
            "sessionId": "think-session",
            "messageId": "turn-think",
        },
        {
            "content": "答案",
            "log": "chat.generate.delta",
            "sessionId": "think-session",
            "messageId": "turn-think",
        },
        {
            "endFlag": True,
            "log": "chat.stream.completed",
            "sessionId": "think-session",
            "messageId": "turn-think",
        },
    ]


def test_non_stream_message_returns_json_response():
    repository = InMemoryConversationRepository()
    expected_session_id = "external-session-1"

    class NonStreamChatService:
        async def complete_user_message(self, actual_conversation_id, content):
            assert actual_conversation_id == expected_session_id
            assert content == "hello"
            return {
                "assistant_message_id": "assistant-1",
                "content": "answer",
                "status": "completed",
            }

    test_app = FastAPI()
    test_app.include_router(create_conversations_router(repository, NonStreamChatService()))
    client = TestClient(test_app)

    response = client.post(
        "/conversations/messages",
        json={
            "sessionId": expected_session_id,
            "streamFlag": "nonStream",
            "query": "hello",
            "messageId": "turn-1",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {"source": "unit"},
        },
    )

    assert response.status_code == 200
    assert repository.get_conversation(expected_session_id).id == expected_session_id
    assert response.json() == {
        "sessionId": expected_session_id,
        "messageId": "turn-1",
        "content": "answer",
        "log": "chat.stream.completed",
        "endFlag": True,
        "payload": {"source": "unit"},
    }


def test_unified_message_rejects_unknown_stream_flag():
    client = TestClient(app)

    response = client.post(
        "/api/conversations/messages",
        json={
            "sessionId": "api-test-invalid-flag",
            "streamFlag": "unknown",
            "query": "hello",
            "messageId": "turn-1",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {},
        },
    )

    assert response.status_code == 422


def test_unified_message_rejects_legacy_account_field():
    client = TestClient(app)

    response = client.post(
        "/api/conversations/messages",
        json={
            "sessionId": "api-test-legacy-account",
            "streamFlag": "nonStream",
            "query": "hello",
            "messageId": "turn-legacy-account",
            "globalUserId": "user-1",
            "Account": "account-1",
            "payload": {},
        },
    )

    assert response.status_code == 422


def test_stream_busy_conversation_returns_conflict():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()

    class BusyChatService:
        def stream_user_message(self, conversation_id, content):
            raise ConversationBusyError(conversation_id)

    test_app = FastAPI()
    test_app.include_router(create_conversations_router(repository, BusyChatService()))
    client = TestClient(test_app)

    response = client.post(
        "/conversations/messages",
        json={
            "sessionId": conversation.id,
            "streamFlag": "stream",
            "query": "hello",
            "messageId": "turn-1",
            "globalUserId": "user-1",
            "userAccount": "account-1",
            "payload": {},
        },
    )

    assert response.status_code == 409
