from threading import RLock

from app.chat.schemas import Conversation, Message, MessageRole, MessageStatus, now_utc


class UnknownConversationError(Exception):
    pass


class UnknownMessageError(Exception):
    pass


class ConversationBusyError(Exception):
    pass


ACTIVE_ASSISTANT_STATUSES = {MessageStatus.STREAMING}


class InMemoryConversationRepository:
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[Message]] = {}
        self._lock = RLock()

    def list_conversations(self) -> list[Conversation]:
        with self._lock:
            return sorted(self._conversations.values(), key=lambda item: item.updated_at, reverse=True)

    def create_conversation(self, conversation_id: str | None = None) -> Conversation:
        with self._lock:
            if conversation_id and conversation_id in self._conversations:
                return self._conversations[conversation_id]
            conversation = Conversation(id=conversation_id) if conversation_id else Conversation()
            self._conversations[conversation.id] = conversation
            self._messages[conversation.id] = []
            return conversation

    def ensure_conversation(self, conversation_id: str | None = None) -> Conversation:
        normalized_id = conversation_id.strip() if conversation_id else ""
        with self._lock:
            if normalized_id and normalized_id in self._conversations:
                return self._conversations[normalized_id]
            return self.create_conversation(normalized_id or None)

    def get_conversation(self, conversation_id: str) -> Conversation:
        with self._lock:
            return self._get_conversation_unlocked(conversation_id)

    def _get_conversation_unlocked(self, conversation_id: str) -> Conversation:
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            raise UnknownConversationError(conversation_id)
        return conversation

    def get_messages(self, conversation_id: str) -> list[Message]:
        with self._lock:
            self._get_conversation_unlocked(conversation_id)
            return list(self._messages[conversation_id])

    def has_active_assistant(self, conversation_id: str) -> bool:
        with self._lock:
            self._get_conversation_unlocked(conversation_id)
            return self._has_active_assistant_unlocked(conversation_id)

    def begin_assistant_turn(self, conversation_id: str, user_content: str) -> tuple[Message, list[dict[str, str]]]:
        with self._lock:
            conversation = self._get_conversation_unlocked(conversation_id)
            if self._has_active_assistant_unlocked(conversation_id):
                raise ConversationBusyError(conversation_id)

            user_message = Message(conversation_id=conversation_id, role=MessageRole.USER, content=user_content)
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="",
                status=MessageStatus.STREAMING,
            )
            self._messages[conversation_id].extend([user_message, assistant_message])
            conversation.updated_at = now_utc()
            history = [
                {"role": message.role.value, "content": message.content}
                for message in self._messages[conversation_id]
                if message.id != assistant_message.id
                and not (message.role == MessageRole.ASSISTANT and message.status in ACTIVE_ASSISTANT_STATUSES)
            ]
            return assistant_message, history

    def get_message(self, conversation_id: str, message_id: str) -> Message:
        with self._lock:
            self._get_conversation_unlocked(conversation_id)
            for message in self._messages[conversation_id]:
                if message.id == message_id:
                    return message
            raise UnknownMessageError(message_id)

    def append_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> Message:
        with self._lock:
            conversation = self._get_conversation_unlocked(conversation_id)
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
            self._get_conversation_unlocked(conversation_id)
            for message in self._messages[conversation_id]:
                if message.id == message_id:
                    if content is not None:
                        message.content = content
                    if status is not None:
                        message.status = status
                    message.updated_at = now_utc()
                    self._conversations[conversation_id].updated_at = now_utc()
                    return message
            raise UnknownMessageError(message_id)

    def _has_active_assistant_unlocked(self, conversation_id: str) -> bool:
        return any(
            message.role == MessageRole.ASSISTANT and message.status in ACTIVE_ASSISTANT_STATUSES
            for message in self._messages[conversation_id]
        )
