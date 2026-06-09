import pytest

from app.chat.schemas import MessageRole, MessageStatus
from app.storage.conversations import InMemoryConversationRepository, UnknownConversationError, UnknownMessageError


def test_create_conversation_and_append_messages():
    repository = InMemoryConversationRepository()

    conversation = repository.create_conversation()
    message = repository.append_message(conversation.id, role=MessageRole.USER, content="hello")

    assert conversation.id
    assert message.role == MessageRole.USER
    assert message.status == MessageStatus.COMPLETED
    assert repository.get_messages(conversation.id)[0].content == "hello"


def test_ensure_conversation_creates_with_requested_id():
    repository = InMemoryConversationRepository()

    conversation = repository.ensure_conversation("external-session-1")
    again = repository.ensure_conversation("external-session-1")

    assert conversation.id == "external-session-1"
    assert again.id == "external-session-1"
    assert len(repository.list_conversations()) == 1


def test_unknown_conversation_raises():
    repository = InMemoryConversationRepository()

    with pytest.raises(UnknownConversationError):
        repository.get_messages("missing")


def test_update_unknown_message_raises_explicit_error():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()

    with pytest.raises(UnknownMessageError):
        repository.update_message(conversation.id, "missing-message", content="nope")
