import pytest

from app.chat.retry import AgentRetryExhaustedError, RetryingAgentRunner


class FailsThenSucceedsRunner:
    def __init__(self) -> None:
        self.calls = 0

    async def stream(self, messages):
        self.calls += 1
        if self.calls < 3:
            raise RuntimeError("tool failed")
        yield {"type": "delta", "content": "ok"}


class AlwaysFailsRunner:
    def __init__(self) -> None:
        self.calls = 0

    async def stream(self, messages):
        self.calls += 1
        raise RuntimeError("skill failed")
        yield


class DeltaThenFailsRunner:
    def __init__(self) -> None:
        self.calls = 0

    async def stream(self, messages):
        self.calls += 1
        yield {"type": "delta", "content": "partial"}
        raise RuntimeError("late failure")


async def test_retrying_agent_runner_retries_until_success_before_delta():
    inner = FailsThenSucceedsRunner()
    runner = RetryingAgentRunner(inner, max_attempts=3)

    events = []
    async for event in runner.stream([{"role": "user", "content": "hi"}]):
        events.append(event)

    assert inner.calls == 3
    assert [event["type"] for event in events] == ["reasoning", "reasoning", "delta"]
    assert events[-1]["content"] == "ok"


async def test_retrying_agent_runner_raises_after_attempts_exhausted():
    inner = AlwaysFailsRunner()
    runner = RetryingAgentRunner(inner, max_attempts=3)

    with pytest.raises(AgentRetryExhaustedError):
        async for _ in runner.stream([{"role": "user", "content": "hi"}]):
            pass

    assert inner.calls == 3


async def test_retrying_agent_runner_does_not_retry_after_delta():
    inner = DeltaThenFailsRunner()
    runner = RetryingAgentRunner(inner, max_attempts=3)

    events = []
    with pytest.raises(RuntimeError, match="late failure"):
        async for event in runner.stream([{"role": "user", "content": "hi"}]):
            events.append(event)

    assert inner.calls == 1
    assert events == [{"type": "delta", "content": "partial"}]
