from fastapi import HTTPException

from app.chat.events import stream_failed
from app.chat.sse import format_sse


def conversation_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Conversation not found.")


def failed_sse(content: str) -> str:
    return format_sse(stream_failed(content))
