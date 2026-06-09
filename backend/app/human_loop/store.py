from threading import RLock
from typing import Any

from app.chat.schemas import now_utc
from app.human_loop.schemas import ApprovalDecisionType, ApprovalRequest, ApprovalStatus


class UnknownApprovalError(Exception):
    pass


class InMemoryApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, ApprovalRequest] = {}
        self._lock = RLock()

    def list_approvals(self) -> list[ApprovalRequest]:
        with self._lock:
            return sorted(self._approvals.values(), key=lambda item: item.created_at, reverse=True)

    def get_approval(self, approval_id: str) -> ApprovalRequest:
        with self._lock:
            approval = self._approvals.get(approval_id)
            if approval is None:
                raise UnknownApprovalError(approval_id)
            return approval

    def create_approval(
        self,
        *,
        tool_name: str,
        description: str,
        payload: dict[str, Any],
        conversation_id: str = "",
        message_id: str = "",
        allowed_decisions: list[ApprovalDecisionType] | None = None,
        node_key: str = "file_write",
    ) -> ApprovalRequest:
        with self._lock:
            approval = ApprovalRequest(
                node_key=node_key,
                conversation_id=conversation_id,
                message_id=message_id,
                tool_name=tool_name,
                description=description,
                payload=payload,
                allowed_decisions=allowed_decisions or [ApprovalDecisionType.APPROVE, ApprovalDecisionType.REJECT],
            )
            self._approvals[approval.id] = approval
            return approval

    def decide(
        self,
        approval_id: str,
        decision: ApprovalDecisionType,
        message: str = "",
    ) -> ApprovalRequest:
        with self._lock:
            approval = self._approvals.get(approval_id)
            if approval is None:
                raise UnknownApprovalError(approval_id)
            approval.status = ApprovalStatus.APPROVED if decision == ApprovalDecisionType.APPROVE else ApprovalStatus.REJECTED
            approval.decision_message = message
            approval.updated_at = now_utc()
            return approval
