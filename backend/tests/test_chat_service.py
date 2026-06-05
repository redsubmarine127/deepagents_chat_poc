import logging

from app.chat.schemas import MessageStatus
from app.chat.retry import AgentRetryExhaustedError
from app.chat.service import ChatService
from app.storage.conversations import InMemoryConversationRepository


class FakeAgentRunner:
    async def stream(self, messages):
        assert messages[-1]["role"] == "user"
        yield {"type": "delta", "content": "hello"}
        yield {"type": "delta", "content": " world"}


async def test_chat_service_streams_and_persists_assistant_message():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = ChatService(repository=repository, agent_runner=FakeAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "reasoning", "delta", "delta", "completed"]
    assert events[1]["content"] == "已创建任务上下文，开始调用 Agent"
    messages = repository.get_messages(conversation.id)
    assert messages[0].content == "hi"
    assert messages[1].content == "hello world"
    assert messages[1].status == MessageStatus.COMPLETED


class FakeReasoningAgentRunner:
    async def stream(self, messages):
        yield {"type": "reasoning", "content": "TodoList: plan created"}
        yield {"type": "delta", "content": "answer"}


class FakeRetryExhaustedAgentRunner:
    async def stream(self, messages):
        raise AgentRetryExhaustedError(attempts=3, cause=RuntimeError("skill failed"))
        yield


async def test_chat_service_forwards_reasoning_without_persisting_it():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = ChatService(repository=repository, agent_runner=FakeReasoningAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "reasoning", "reasoning", "delta", "completed"]
    assert events[1]["content"] == "已创建任务上下文，开始调用 Agent"
    assert events[2]["content"] == "TodoList: plan created"
    messages = repository.get_messages(conversation.id)
    assert messages[1].content == "answer"


async def test_chat_service_logs_lifecycle_with_bounded_content(caplog):
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = ChatService(repository=repository, agent_runner=FakeAgentRunner())
    user_content = "hello " + ("x" * 160)

    caplog.set_level(logging.INFO, logger="app.chat.service")

    async for _ in service.stream_user_message(conversation.id, user_content):
        pass

    log_text = "\n".join(record.getMessage() for record in caplog.records)
    assert "chat.stream.start" in log_text
    assert "chat.stream.delta" in log_text
    assert "chat.stream.completed" in log_text
    assert user_content not in log_text


async def test_chat_service_returns_retry_message_after_agent_exhaustion():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = ChatService(repository=repository, agent_runner=FakeRetryExhaustedAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert events[-1]["type"] == "failed"
    assert "请稍后重试" in events[-1]["content"]
    messages = repository.get_messages(conversation.id)
    assert messages[1].status == MessageStatus.FAILED
    assert "请稍后重试" in messages[1].content
