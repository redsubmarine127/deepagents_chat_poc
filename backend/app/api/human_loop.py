from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.errors import failed_sse
from app.chat.service import ChatService
from app.chat.sse import format_sse
from app.human_loop.schemas import (
    ApprovalDecisionType,
    ApprovalResponse,
    CreateApprovalRequest,
    RejectApprovalRequest,
    to_approval_response,
)
from app.human_loop.store import InMemoryApprovalStore, UnknownApprovalError


def create_router(approval_store: InMemoryApprovalStore, chat_service: ChatService) -> APIRouter:
    router = APIRouter()

    @router.get("/human-loop/approvals")
    def list_approvals() -> list[ApprovalResponse]:
        return [to_approval_response(approval) for approval in approval_store.list_approvals()]

    @router.post("/human-loop/approvals")
    def create_approval(request: CreateApprovalRequest) -> ApprovalResponse:
        approval = approval_store.create_approval(
            tool_name=request.toolName,
            description=request.description,
            payload=request.payload,
            node_key=request.nodeKey,
        )
        return to_approval_response(approval)

    @router.post("/human-loop/approvals/{approval_id}/approve")
    def approve(approval_id: str) -> ApprovalResponse:
        try:
            return to_approval_response(approval_store.decide(approval_id, ApprovalDecisionType.APPROVE))
        except UnknownApprovalError as exc:
            raise HTTPException(status_code=404, detail="Approval not found.") from exc

    @router.post("/human-loop/approvals/{approval_id}/reject")
    def reject(approval_id: str, request: RejectApprovalRequest | None = None) -> ApprovalResponse:
        try:
            return to_approval_response(
                approval_store.decide(
                    approval_id,
                    ApprovalDecisionType.REJECT,
                    message=request.message if request else "用户拒绝执行该操作。",
                )
            )
        except UnknownApprovalError as exc:
            raise HTTPException(status_code=404, detail="Approval not found.") from exc

    @router.post("/human-loop/approvals/{approval_id}/approve/stream")
    async def approve_stream(approval_id: str):
        return _decision_stream(chat_service, approval_id, ApprovalDecisionType.APPROVE)

    @router.post("/human-loop/approvals/{approval_id}/reject/stream")
    async def reject_stream(approval_id: str, request: RejectApprovalRequest | None = None):
        message = request.message if request else "用户拒绝执行该操作。"
        return _decision_stream(chat_service, approval_id, ApprovalDecisionType.REJECT, message=message)

    return router


def _decision_stream(
    chat_service: ChatService,
    approval_id: str,
    decision: ApprovalDecisionType,
    *,
    message: str = "",
) -> StreamingResponse:
    async def event_stream():
        try:
            async for chat_event in chat_service.stream_approval_decision(approval_id, decision, message=message):
                yield format_sse(chat_event)
        except UnknownApprovalError:
            yield failed_sse("Approval not found.")
        except ValueError as exc:
            yield failed_sse(str(exc))

    return StreamingResponse(event_stream(), media_type="text/event-stream")
