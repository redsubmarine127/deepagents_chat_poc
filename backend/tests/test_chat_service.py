from app.chat.schemas import MessageStatus
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
