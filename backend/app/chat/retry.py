from collections.abc import AsyncIterator
import logging
from typing import Protocol

from app.chat.events import ChatStreamEvent, ChatStreamEventType, stream_reasoning
from app.observability import summarize_text

logger = logging.getLogger(__name__)


class AgentRetryExhaustedError(Exception):
    def __init__(self, attempts: int, cause: Exception) -> None:
        self.attempts = attempts
        self.cause = cause
        super().__init__(f"Agent execution failed after {attempts} attempts: {cause}")


class AgentRunner(Protocol):
    async def stream(
        self,
        messages: list[dict[str, str]],
        *,
        thread_id: str | None = None,
    ) -> AsyncIterator[ChatStreamEvent]:
        pass


class RetryingAgentRunner:
    def __init__(self, runner: AgentRunner, max_attempts: int = 3) -> None:
        self._runner = runner
        self._max_attempts = max(1, max_attempts)

    async def stream(
        self,
        messages: list[dict[str, str]],
        *,
        thread_id: str | None = None,
    ) -> AsyncIterator[ChatStreamEvent]:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            emitted_delta = False
            try:
                logger.info("agent.retry.attempt_start attempt=%d max_attempts=%d", attempt, self._max_attempts)
                async for chat_event in self._runner.stream(messages, thread_id=thread_id):
                    if chat_event.get("type") == ChatStreamEventType.DELTA:
                        emitted_delta = True
                    yield chat_event
                logger.info("agent.retry.attempt_success attempt=%d max_attempts=%d", attempt, self._max_attempts)
                return
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "agent.retry.attempt_failed attempt=%d max_attempts=%d emitted_delta=%s error_type=%s error=%s",
                    attempt,
                    self._max_attempts,
                    emitted_delta,
                    type(exc).__name__,
                    summarize_text(str(exc)),
                )
                if emitted_delta:
                    raise
                if attempt < self._max_attempts:
                    yield stream_reasoning(f"Agent 执行失败，正在重试 {attempt + 1}/{self._max_attempts}")

        raise AgentRetryExhaustedError(self._max_attempts, last_error or RuntimeError("unknown agent failure"))
