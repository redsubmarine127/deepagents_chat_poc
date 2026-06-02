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
