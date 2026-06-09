from dataclasses import dataclass
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver

from app.chat.agent import LazyDeepAgentRunner
from app.chat.retry import RetryingAgentRunner
from app.chat.service import ChatService
from app.config import Settings
from app.human_loop.config import build_interrupt_on
from app.human_loop.store import InMemoryApprovalStore
from app.skills.loader import discover_skills
from app.skills.schemas import SkillMetadata
from app.storage.conversations import InMemoryConversationRepository
from app.tools.loader import ToolCatalog, empty_tool_catalog, load_tool_catalog


@dataclass
class AppRuntime:
    repository: InMemoryConversationRepository
    approval_store: InMemoryApprovalStore
    chat_service: ChatService
    skills: list[SkillMetadata]
    tool_catalog: ToolCatalog


def build_runtime(settings: Settings, project_root: Path) -> AppRuntime:
    repository = InMemoryConversationRepository()
    approval_store = InMemoryApprovalStore()
    tool_catalog = load_tool_catalog(project_root, settings.tools_dir) if settings.tools_enabled else empty_tool_catalog()
    checkpointer = InMemorySaver()
    interrupt_on = build_interrupt_on() if settings.human_loop_enabled else None
    agent_runner = RetryingAgentRunner(
        LazyDeepAgentRunner(
            settings,
            project_root=project_root,
            tools=tool_catalog.tools,
            interrupt_on=interrupt_on,
            checkpointer=checkpointer,
        ),
        max_attempts=settings.agent_max_retries,
    )
    chat_service = ChatService(
        repository=repository,
        agent_runner=agent_runner,
        approval_store=approval_store,
    )
    skills = discover_skills(project_root, settings.skills_dir) if settings.skills_enabled else []
    return AppRuntime(
        repository=repository,
        approval_store=approval_store,
        chat_service=chat_service,
        skills=skills,
        tool_catalog=tool_catalog,
    )
