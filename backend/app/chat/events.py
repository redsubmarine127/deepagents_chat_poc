from enum import StrEnum
from typing import Any, NotRequired, TypedDict


class ChatStreamEventType(StrEnum):
    STARTED = "started"
    REASONING = "reasoning"
    DELTA = "delta"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatStreamEvent(TypedDict):
    type: str
    content: str
    # Agent-level events do not know the persisted assistant message id; ChatService adds it before SSE output.
    messageId: NotRequired[str]


class ChatApiEvent(TypedDict, total=False):
    state: str
    stateDesc: str
    content: str
    processResult: dict[str, Any]
    searchList: list[dict[str, Any]]
    log: str
    endFlag: bool
    error: str
    sessionId: str
    messageId: str
    payload: NotRequired[dict[str, Any]]


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


class ChatApiEventFormatter:
    def __init__(self, *, session_id: str, request_message_id: str) -> None:
        self._session_id = session_id
        self._request_message_id = request_message_id
        self._thinking_started = False
        self._generate_started = False

    def format(self, event: ChatStreamEvent) -> list[ChatApiEvent]:
        event_type = event.get("type", "")
        content = event.get("content", "")

        if event_type == ChatStreamEventType.STARTED:
            return [self._thinking_start("chat.stream.started")]

        if event_type == ChatStreamEventType.REASONING:
            return [*self._ensure_thinking_started(), self._thinking_delta(content)]

        if event_type == ChatStreamEventType.DELTA:
            return [*self._ensure_generate_started(), self._generate_delta(content)]

        if event_type == ChatStreamEventType.COMPLETED:
            return [self._base_event(endFlag=True, log="chat.stream.completed")]

        if event_type == ChatStreamEventType.FAILED:
            return [self._base_event(error=content, endFlag=True, log="chat.stream.failed")]

        return []

    def _ensure_thinking_started(self) -> list[ChatApiEvent]:
        if self._thinking_started:
            return []
        return [self._thinking_start("chat.thinking.start")]

    def _ensure_generate_started(self) -> list[ChatApiEvent]:
        if self._generate_started:
            return []
        self._generate_started = True
        return [self._base_event(state="GENERATE", stateDesc="生成答案", log="chat.generate.start")]

    def _thinking_start(self, log: str) -> ChatApiEvent:
        self._thinking_started = True
        return self._base_event(state="THINKING", stateDesc="思考中", log=log)

    def _thinking_delta(self, content: str) -> ChatApiEvent:
        return self._base_event(
            content=_wrap_think(content),
            processResult={"content": content} if content else {},
            log="chat.thinking.delta",
        )

    def _generate_delta(self, content: str) -> ChatApiEvent:
        return self._base_event(content=content, log="chat.generate.delta")

    def _base_event(self, **values: Any) -> ChatApiEvent:
        return _compact_mapping(
            {
                "sessionId": self._session_id,
                "messageId": self._request_message_id,
                **values,
            }
        )


def to_chat_api_response(
    *,
    session_id: str,
    request_message_id: str,
    content: str,
    status: str,
) -> dict[str, Any]:
    is_failed = status == "failed"
    return _compact_mapping(
        {
            "sessionId": session_id,
            "messageId": request_message_id,
            "content": "" if is_failed else content,
            "searchList": [],
            "log": "chat.stream.failed" if is_failed else "chat.stream.completed",
            "endFlag": True,
            "error": content if is_failed else "",
        }
    )


def _wrap_think(content: str) -> str:
    return f"<think>{content}</think>" if content else ""


def _compact_mapping(values: dict[str, Any]) -> ChatApiEvent:
    compacted = {}
    for key, value in values.items():
        if value is None or value == "" or value == {} or value == [] or value is False:
            continue
        compacted[key] = value
    return compacted
