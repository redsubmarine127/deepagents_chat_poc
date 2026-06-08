from app.human_loop.config import build_interrupt_on
from app.human_loop.schemas import ApprovalDecisionType
from app.human_loop.store import InMemoryApprovalStore


def test_build_interrupt_on_requires_write_approval():
    interrupt_on = build_interrupt_on()

    assert set(interrupt_on.keys()) == {"write_file", "edit_file"}
    assert interrupt_on["write_file"]["allowed_decisions"] == ["approve", "reject"]


def test_approval_store_approve_and_reject():
    store = InMemoryApprovalStore()
    approval = store.create_approval(tool_name="write_file", description="Write /tmp/a.txt", payload={"path": "/tmp/a.txt"})

    approved = store.decide(approval.id, ApprovalDecisionType.APPROVE)

    assert approved.status == "approved"

    second = store.create_approval(tool_name="edit_file", description="Edit file", payload={})
    rejected = store.decide(second.id, ApprovalDecisionType.REJECT, message="No")

    assert rejected.status == "rejected"
    assert rejected.decision_message == "No"
