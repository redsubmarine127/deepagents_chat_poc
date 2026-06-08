from enum import StrEnum
from typing import NotRequired, TypedDict


class ChatStreamEventType(StrEnum):
    STARTED = "started"
    REASONING = "reasoning"
    DELTA = "delta"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVAL_REQUIRED = "approval_required"


class ChatStreamEvent(TypedDict):
    type: str
    content: str
    # Agent-level events do not know the persisted assistant message id; ChatService adds it before SSE output.
    messageId: NotRequired[str]
    approvalId: NotRequired[str]
    toolName: NotRequired[str]


def stream_event(
    event_type: ChatStreamEventType,
    content: str = "",
    *,
    message_id: str | None = None,
) -> ChatStreamEvent:
    payload: ChatStreamEvent = {"type": event_type.value, "content": content}
    if message_id is not None:
        payload["messageId"] = message_id
    return payload


def stream_started(message_id: str) -> ChatStreamEvent:
    return stream_event(ChatStreamEventType.STARTED, message_id=message_id)


def stream_reasoning(content: str, *, message_id: str | None = None) -> ChatStreamEvent:
    return stream_event(ChatStreamEventType.REASONING, content, message_id=message_id)


def stream_delta(content: str, *, message_id: str | None = None) -> ChatStreamEvent:
    return stream_event(ChatStreamEventType.DELTA, content, message_id=message_id)


def stream_completed(content: str, *, message_id: str) -> ChatStreamEvent:
    return stream_event(ChatStreamEventType.COMPLETED, content, message_id=message_id)


def stream_failed(content: str, *, message_id: str = "") -> ChatStreamEvent:
    return stream_event(ChatStreamEventType.FAILED, content, message_id=message_id)


def stream_approval_required(
    content: str,
    *,
    approval_id: str,
    tool_name: str,
    message_id: str | None = None,
) -> ChatStreamEvent:
    payload = stream_event(ChatStreamEventType.APPROVAL_REQUIRED, content, message_id=message_id)
    payload["approvalId"] = approval_id
    payload["toolName"] = tool_name
    return payload
