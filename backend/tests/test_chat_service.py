import logging

from app.chat.schemas import MessageStatus
from app.chat.retry import AgentRetryExhaustedError
from app.chat.service import ChatService
from app.human_loop.schemas import ApprovalDecisionType
from app.human_loop.store import InMemoryApprovalStore
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository


class FakeAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        assert messages[-1]["role"] == "user"
        assert thread_id
        yield {"type": "delta", "content": "hello"}
        yield {"type": "delta", "content": " world"}

    async def resume(self, decisions, *, thread_id):
        yield {"type": "delta", "content": " resumed"}


def make_service(repository, agent_runner, approval_store=None):
    return ChatService(
        repository=repository,
        agent_runner=agent_runner,
        approval_store=approval_store or InMemoryApprovalStore(),
    )


async def test_chat_service_streams_and_persists_assistant_message():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "reasoning", "delta", "delta", "completed"]
    assert events[1]["content"] == "已创建任务上下文，开始调用 Agent"
    messages = repository.get_messages(conversation.id)
    assert messages[0].content == "hi"
    assert messages[1].content == "hello world"
    assert messages[1].status == MessageStatus.COMPLETED


def test_chat_service_rejects_new_message_when_conversation_is_active():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    repository.begin_assistant_turn(conversation.id, "already running")
    service = make_service(repository, FakeAgentRunner())

    try:
        service.stream_user_message(conversation.id, "hi")
    except ConversationBusyError:
        pass
    else:
        raise AssertionError("Expected active conversation to reject a new message")


class FakeReasoningAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        yield {"type": "reasoning", "content": "TodoList: plan created"}
        yield {"type": "delta", "content": "answer"}

    async def resume(self, decisions, *, thread_id):
        yield {"type": "delta", "content": "resumed"}


class FakeRetryExhaustedAgentRunner:
    async def stream(self, messages, *, thread_id=None):
        raise AgentRetryExhaustedError(attempts=3, cause=RuntimeError("skill failed"))
        yield

    async def resume(self, decisions, *, thread_id):
        raise AgentRetryExhaustedError(attempts=3, cause=RuntimeError("skill failed"))
        yield


class FakeApprovalAgentRunner:
    def __init__(self) -> None:
        self.resume_decisions = []

    async def stream(self, messages, *, thread_id=None):
        yield {
            "type": "approval_required",
            "content": "Review file write",
            "toolName": "write_file",
            "payload": {"path": "/tmp/a.txt"},
            "allowedDecisions": ["approve", "reject"],
        }

    async def resume(self, decisions, *, thread_id):
        self.resume_decisions.append((thread_id, decisions))
        yield {"type": "delta", "content": "done after approval"}


async def test_chat_service_forwards_reasoning_without_persisting_it():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeReasoningAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert [event["type"] for event in events] == ["started", "reasoning", "reasoning", "delta", "completed"]
    assert events[1]["content"] == "已创建任务上下文，开始调用 Agent"
    assert events[2]["content"] == "TodoList: plan created"
    messages = repository.get_messages(conversation.id)
    assert messages[1].content == "answer"


async def test_chat_service_logs_lifecycle_with_bounded_content(caplog):
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeAgentRunner())
    user_content = "hello " + ("x" * 160)

    caplog.set_level(logging.INFO, logger="app.chat.service")

    async for _ in service.stream_user_message(conversation.id, user_content):
        pass

    log_text = "\n".join(record.getMessage() for record in caplog.records)
    assert "chat.stream.start" in log_text
    assert "chat.stream.delta" in log_text
    assert "chat.stream.completed" in log_text
    assert user_content not in log_text


async def test_chat_service_returns_retry_message_after_agent_exhaustion():
    repository = InMemoryConversationRepository()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeRetryExhaustedAgentRunner())

    events = []
    async for event in service.stream_user_message(conversation.id, "hi"):
        events.append(event)

    assert events[-1]["type"] == "failed"
    assert "请稍后重试" in events[-1]["content"]
    messages = repository.get_messages(conversation.id)
    assert messages[1].status == MessageStatus.FAILED
    assert "请稍后重试" in messages[1].content


async def test_chat_service_persists_agent_approval_request():
    repository = InMemoryConversationRepository()
    approval_store = InMemoryApprovalStore()
    conversation = repository.create_conversation()
    service = make_service(repository, FakeApprovalAgentRunner(), approval_store)

    events = []
    async for event in service.stream_user_message(conversation.id, "write a file"):
        events.append(event)

    assert events[-1]["type"] == "approval_required"
    approval_id = events[-1]["approvalId"]
    approval = approval_store.get_approval(approval_id)
    assert approval.conversation_id == conversation.id
    assert approval.message_id == events[0]["messageId"]
    assert approval.payload == {"path": "/tmp/a.txt"}
    assert repository.get_message(conversation.id, approval.message_id).status == MessageStatus.PENDING_APPROVAL


async def test_chat_service_resumes_after_approval_decision():
    repository = InMemoryConversationRepository()
    approval_store = InMemoryApprovalStore()
    runner = FakeApprovalAgentRunner()
    conversation = repository.create_conversation()
    service = make_service(repository, runner, approval_store)

    async for _ in service.stream_user_message(conversation.id, "write a file"):
        pass
    approval = approval_store.list_approvals()[0]

    events = []
    async for event in service.stream_approval_decision(approval.id, ApprovalDecisionType.APPROVE):
        events.append(event)

    assert runner.resume_decisions == [(conversation.id, [{"type": "approve"}])]
    assert [event["type"] for event in events] == ["delta", "completed"]
    assert repository.get_message(conversation.id, approval.message_id).content == "done after approval"
