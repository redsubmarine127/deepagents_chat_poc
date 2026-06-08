from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.chat.schemas import now_utc


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalDecisionType(StrEnum):
    APPROVE = "approve"
    REJECT = "reject"


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    node_key: str = "file_write"
    tool_name: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_message: str = ""
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class CreateApprovalRequest(BaseModel):
    toolName: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    nodeKey: str = "file_write"


class ApprovalResponse(BaseModel):
    id: str
    nodeKey: str
    toolName: str
    description: str
    payload: dict[str, Any]
    status: ApprovalStatus
    decisionMessage: str
    createdAt: datetime
    updatedAt: datetime


class RejectApprovalRequest(BaseModel):
    message: str = "用户拒绝执行该操作。"


def to_approval_response(approval: ApprovalRequest) -> ApprovalResponse:
    return ApprovalResponse(
        id=approval.id,
        nodeKey=approval.node_key,
        toolName=approval.tool_name,
        description=approval.description,
        payload=approval.payload,
        status=approval.status,
        decisionMessage=approval.decision_message,
        createdAt=approval.created_at,
        updatedAt=approval.updated_at,
    )
