from collections.abc import AsyncIterator
from typing import Protocol

from app.chat.events import (
    ChatStreamEvent,
    ChatStreamEventType,
    stream_completed,
    stream_delta,
    stream_failed,
    stream_reasoning,
    stream_started,
)
from app.chat.schemas import MessageRole, MessageStatus
from app.storage.conversations import InMemoryConversationRepository


class AgentRunner(Protocol):
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[ChatStreamEvent]:
        pass


class ChatService:
    def __init__(self, repository: InMemoryConversationRepository, agent_runner: AgentRunner) -> None:
        self._repository = repository
        self._agent_runner = agent_runner

    async def stream_user_message(self, conversation_id: str, content: str) -> AsyncIterator[ChatStreamEvent]:
        text = content.strip()
        if not text:
            raise ValueError("Message content is required.")

        self._repository.append_message(conversation_id, role=MessageRole.USER, content=text)
        assistant = self._repository.append_message(
            conversation_id,
            role=MessageRole.ASSISTANT,
            content="",
            status=MessageStatus.STREAMING,
        )
        yield stream_started(assistant.id)
        yield stream_reasoning("已创建任务上下文，开始调用 Agent", message_id=assistant.id)

        chunks: list[str] = []
        history = [
            {"role": message.role.value, "content": message.content}
            for message in self._repository.get_messages(conversation_id)
            if message.id != assistant.id
        ]

        try:
            async for chat_event in self._agent_runner.stream(history):
                event_type = chat_event.get("type")
                content_chunk = chat_event.get("content", "")
                if event_type == ChatStreamEventType.REASONING:
                    # Reasoning traces are live execution metadata for the UI, not assistant answer text.
                    yield stream_reasoning(content_chunk, message_id=assistant.id)
                    continue
                if event_type != ChatStreamEventType.DELTA:
                    continue

                chunks.append(content_chunk)
                yield stream_delta(content_chunk, message_id=assistant.id)

            final_content = "".join(chunks)
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=final_content,
                status=MessageStatus.COMPLETED,
            )
            yield stream_completed(final_content, message_id=assistant.id)
        except Exception as exc:
            failure = f"Assistant generation failed: {exc}"
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=failure,
                status=MessageStatus.FAILED,
            )
            yield stream_failed(failure, message_id=assistant.id)
