from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def now_utc() -> datetime:
    return datetime.now(UTC)


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageStatus(StrEnum):
    STREAMING = "streaming"
    COMPLETED = "completed"
    FAILED = "failed"


class StreamFlag(StrEnum):
    STREAM = "stream"
    NON_STREAM = "nonStream"


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = "New conversation"
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    conversation_id: str
    role: MessageRole
    content: str
    status: MessageStatus = MessageStatus.COMPLETED
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class ConversationResponse(BaseModel):
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime


class MessageResponse(BaseModel):
    id: str
    conversationId: str
    role: MessageRole
    content: str
    status: MessageStatus
    createdAt: datetime
    updatedAt: datetime


class ChatMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sessionId: str = ""
    streamFlag: StreamFlag
    query: str = Field(min_length=1)
    messageId: str = Field(min_length=1)
    globalUserId: str = ""
    userAccount: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatMessageResponse(BaseModel):
    sessionId: str
    messageId: str
    state: str = ""
    stateDesc: str = ""
    content: str = ""
    processResult: dict[str, Any] = Field(default_factory=dict)
    searchList: list[dict[str, Any]] = Field(default_factory=list)
    log: str = ""
    endFlag: str | bool = ""
    error: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


def to_conversation_response(conversation: Conversation) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        createdAt=conversation.created_at,
        updatedAt=conversation.updated_at,
    )


def to_message_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversationId=message.conversation_id,
        role=message.role,
        content=message.content,
        status=message.status,
        createdAt=message.created_at,
        updatedAt=message.updated_at,
    )
