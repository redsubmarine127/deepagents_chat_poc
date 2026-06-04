from collections.abc import AsyncIterator
import logging
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
from app.observability import summarize_text
from app.storage.conversations import InMemoryConversationRepository

logger = logging.getLogger(__name__)


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

        logger.info(
            "chat.stream.start conversation_id=%s user_content_length=%d user_preview=%s",
            conversation_id,
            len(text),
            summarize_text(text),
        )
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
        logger.info(
            "chat.stream.context conversation_id=%s assistant_message_id=%s history_count=%d",
            conversation_id,
            assistant.id,
            len(history),
        )

        try:
            chunk_count = 0
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
                chunk_count += 1
                logger.info(
                    "chat.stream.delta conversation_id=%s assistant_message_id=%s chunk_index=%d chunk_length=%d chunk_preview=%s",
                    conversation_id,
                    assistant.id,
                    chunk_count,
                    len(content_chunk),
                    summarize_text(content_chunk, limit=80),
                )
                yield stream_delta(content_chunk, message_id=assistant.id)

            final_content = "".join(chunks)
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=final_content,
                status=MessageStatus.COMPLETED,
            )
            logger.info(
                "chat.stream.completed conversation_id=%s assistant_message_id=%s chunk_count=%d assistant_content_length=%d assistant_preview=%s",
                conversation_id,
                assistant.id,
                chunk_count,
                len(final_content),
                summarize_text(final_content),
            )
            yield stream_completed(final_content, message_id=assistant.id)
        except Exception as exc:
            failure = f"Assistant generation failed: {exc}"
            logger.exception(
                "chat.stream.failed conversation_id=%s assistant_message_id=%s error_type=%s error=%s",
                conversation_id,
                assistant.id,
                type(exc).__name__,
                summarize_text(str(exc)),
            )
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=failure,
                status=MessageStatus.FAILED,
            )
            yield stream_failed(failure, message_id=assistant.id)
