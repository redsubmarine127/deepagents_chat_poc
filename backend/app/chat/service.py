from collections.abc import AsyncIterator
import logging
from typing import Any, Protocol

from app.chat.events import (
    ChatStreamEvent,
    ChatStreamEventType,
    stream_completed,
    stream_delta,
    stream_failed,
    stream_reasoning,
    stream_started,
)
from app.chat.retry import AgentRetryExhaustedError
from app.chat.schemas import MessageStatus
from app.observability import summarize_text
from app.storage.conversations import InMemoryConversationRepository

logger = logging.getLogger(__name__)


class AgentRunner(Protocol):
    async def stream(
        self,
        messages: list[dict[str, str]],
        *,
        thread_id: str | None = None,
    ) -> AsyncIterator[ChatStreamEvent]:
        pass


class ChatService:
    def __init__(
        self,
        repository: InMemoryConversationRepository,
        agent_runner: AgentRunner,
    ) -> None:
        self._repository = repository
        self._agent_runner = agent_runner

    def stream_user_message(self, conversation_id: str, content: str) -> AsyncIterator[ChatStreamEvent]:
        text = content.strip()
        if not text:
            raise ValueError("Message content is required.")

        logger.info(
            "chat.stream.start conversation_id=%s user_content_length=%d user_preview=%s",
            conversation_id,
            len(text),
            summarize_text(text),
        )
        assistant, history = self._repository.begin_assistant_turn(conversation_id, text)
        logger.info(
            "chat.stream.context conversation_id=%s assistant_message_id=%s history_count=%d",
            conversation_id,
            assistant.id,
            len(history),
        )
        return self._stream_prepared_user_message(conversation_id, assistant.id, history)

    async def complete_user_message(self, conversation_id: str, content: str) -> dict[str, Any]:
        assistant_message_id = ""
        final_content = ""
        status = MessageStatus.COMPLETED

        async for event in self.stream_user_message(conversation_id, content):
            if event.get("messageId"):
                assistant_message_id = event["messageId"]

            event_type = event.get("type")
            if event_type == ChatStreamEventType.COMPLETED:
                final_content = event.get("content", "")
                status = MessageStatus.COMPLETED
            elif event_type == ChatStreamEventType.FAILED:
                final_content = event.get("content", "")
                status = MessageStatus.FAILED

        return {
            "assistant_message_id": assistant_message_id,
            "content": final_content,
            "status": status,
        }

    async def _stream_prepared_user_message(
        self,
        conversation_id: str,
        assistant_message_id: str,
        history: list[dict[str, str]],
    ) -> AsyncIterator[ChatStreamEvent]:
        yield stream_started(assistant_message_id)
        yield stream_reasoning("已创建任务上下文，开始调用 Agent", message_id=assistant_message_id)
        try:
            agent_events = self._agent_runner.stream(history, thread_id=conversation_id)
            async for chat_event in self._relay_agent_events(conversation_id, assistant_message_id, agent_events):
                yield chat_event
        except Exception as exc:
            async for failure_event in self._handle_stream_failure(conversation_id, assistant_message_id, exc):
                yield failure_event

    async def _relay_agent_events(
        self,
        conversation_id: str,
        assistant_message_id: str,
        agent_events: AsyncIterator[ChatStreamEvent],
    ) -> AsyncIterator[ChatStreamEvent]:
        chunks: list[str] = []
        chunk_count = 0
        async for chat_event in agent_events:
            event_type = chat_event.get("type")
            content_chunk = chat_event.get("content", "")
            if event_type == ChatStreamEventType.REASONING:
                # Reasoning traces are live execution metadata for the UI, not assistant answer text.
                yield stream_reasoning(content_chunk, message_id=assistant_message_id)
                continue
            if event_type != ChatStreamEventType.DELTA:
                continue

            chunks.append(content_chunk)
            chunk_count += 1
            logger.info(
                "chat.stream.delta conversation_id=%s assistant_message_id=%s chunk_index=%d chunk_length=%d chunk_preview=%s",
                conversation_id,
                assistant_message_id,
                chunk_count,
                len(content_chunk),
                summarize_text(content_chunk, limit=80),
            )
            yield stream_delta(content_chunk, message_id=assistant_message_id)

        current_message = self._repository.get_message(conversation_id, assistant_message_id)
        final_content = current_message.content + "".join(chunks)
        self._repository.update_message(
            conversation_id,
            assistant_message_id,
            content=final_content,
            status=MessageStatus.COMPLETED,
        )
        logger.info(
            "chat.stream.completed conversation_id=%s assistant_message_id=%s chunk_count=%d assistant_content_length=%d assistant_preview=%s",
            conversation_id,
            assistant_message_id,
            chunk_count,
            len(final_content),
            summarize_text(final_content),
        )
        yield stream_completed(final_content, message_id=assistant_message_id)

    async def _handle_stream_failure(
        self,
        conversation_id: str,
        assistant_message_id: str,
        exc: Exception,
    ) -> AsyncIterator[ChatStreamEvent]:
        if isinstance(exc, AgentRetryExhaustedError):
            failure = "生成失败，Agent 调用工具或 Skill 多次失败，请稍后重试。"
        else:
            failure = f"生成失败，请稍后重试。错误信息：{exc}"
        logger.exception(
            "chat.stream.failed conversation_id=%s assistant_message_id=%s error_type=%s error=%s",
            conversation_id,
            assistant_message_id,
            type(exc).__name__,
            summarize_text(str(exc)),
        )
        self._repository.update_message(
            conversation_id,
            assistant_message_id,
            content=failure,
            status=MessageStatus.FAILED,
        )
        yield stream_failed(failure, message_id=assistant_message_id)
