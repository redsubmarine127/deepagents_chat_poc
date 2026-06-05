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


def test_unknown_conversation_raises():
    repository = InMemoryConversationRepository()

    with pytest.raises(UnknownConversationError):
        repository.get_messages("missing")


def test_update_unknown_message_raises_explicit_error():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()

    with pytest.raises(UnknownMessageError):
        repository.update_message(conversation.id, "missing-message", content="nope")
