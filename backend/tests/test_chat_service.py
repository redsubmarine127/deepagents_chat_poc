import logging

from app.chat.schemas import MessageStatus
from app.chat.retry import AgentRetryExhaustedError
from app.chat.service import ChatService
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository


class FakeAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        assert messages[-1]["role"] == "user"
        assert thread_id
        yield {"type": "delta", "content": "hello"}
        yield {"type": "delta", "content": " world"}

def make_service(repository, agent_runner):
    return ChatService(
        repository=repository,
        agent_runner=agent_runner,
    )


async def test_chat_service_streams_and_persists_assistant_message():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "reasoning", "delta", "delta", "completed"]
    assert events[1]["content"] == "已创建任务上下文，开始调用 Agent"
    messages = repository.get_messages(conversation.id)
    assert messages[0].content == "hi"
    assert messages[1].content == "hello world"
    assert messages[1].status == MessageStatus.COMPLETED


async def test_chat_service_completes_user_message_without_sse():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeAgentRunner())

    result = await service.complete_user_message(conversation.id, "hi")

    assert result["content"] == "hello world"
    assert result["status"] == MessageStatus.COMPLETED
    assert result["assistant_message_id"] == repository.get_messages(conversation.id)[1].id


def test_chat_service_rejects_new_message_when_conversation_is_active():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    repository.begin_assistant_turn(conversation.id, "already running")
    service = make_service(repository, FakeAgentRunner())

    try:
        service.stream_user_message(conversation.id, "hi")
    except ConversationBusyError:
        pass
    else:
        raise AssertionError("Expected active conversation to reject a new message")


class FakeReasoningAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        yield {"type": "reasoning", "content": "TodoList: plan created"}
        yield {"type": "delta", "content": "answer"}


class FakeRetryExhaustedAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        raise AgentRetryExhaustedError(attempts=3, cause=RuntimeError("skill failed"))
        yield

async def test_chat_service_forwards_reasoning_without_persisting_it():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeReasoningAgentRunner())

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
    service = make_service(repository, FakeAgentRunner())
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
    service = make_service(repository, FakeRetryExhaustedAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert events[-1]["type"] == "failed"
    assert "请稍后重试" in events[-1]["content"]
    messages = repository.get_messages(conversation.id)
    assert messages[1].status == MessageStatus.FAILED
    assert "请稍后重试" in messages[1].content
