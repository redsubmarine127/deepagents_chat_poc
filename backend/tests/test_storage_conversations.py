from datetime import UTC, datetime

from app.chat.schemas import MessageRole, MessageStatus
from app.storage import conversations as conversations_module
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository


def test_begin_assistant_turn_rejects_active_assistant():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    repository.append_message(
        conversation.id,
        role=MessageRole.ASSISTANT,
        content="",
        status=MessageStatus.STREAMING,
    )

    try:
        repository.begin_assistant_turn(conversation.id, "hi")
    except ConversationBusyError:
        pass
    else:
        raise AssertionError("Expected active conversation to reject a new assistant turn")


def test_update_message_refreshes_conversation_order(monkeypatch):
    times = iter(
        [
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 1, 2, tzinfo=UTC),
            datetime(2026, 1, 3, tzinfo=UTC),
            datetime(2026, 1, 4, tzinfo=UTC),
        ]
    )
    monkeypatch.setattr(conversations_module, "now_utc", lambda: next(times))
    repository = InMemoryConversationRepository()
    first = repository.create_conversation()
    first_message = repository.append_message(first.id, role=MessageRole.ASSISTANT, content="old")
    second = repository.create_conversation()
    first.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    second.updated_at = datetime(2026, 1, 2, tzinfo=UTC)

    assert repository.list_conversations()[0].id == second.id

    repository.update_message(first.id, first_message.id, content="new")

    assert repository.list_conversations()[0].id == first.id
