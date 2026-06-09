from dataclasses import dataclass
from pathlib import Path

from app.chat.agent import LazyDeepAgentRunner
from app.chat.retry import RetryingAgentRunner
from app.chat.service import ChatService
from app.config import Settings
from app.skills.loader import discover_skills
from app.skills.schemas import SkillMetadata
from app.storage.conversations import InMemoryConversationRepository
from app.tools.loader import ToolCatalog, empty_tool_catalog, load_tool_catalog


@dataclass
class AppRuntime:
    repository: InMemoryConversationRepository
    chat_service: ChatService
    skills: list[SkillMetadata]
    tool_catalog: ToolCatalog


def build_runtime(settings: Settings, project_root: Path) -> AppRuntime:
    repository = InMemoryConversationRepository()
    tool_catalog = load_tool_catalog(project_root, settings.tools_dir) if settings.tools_enabled else empty_tool_catalog()
    agent_runner = RetryingAgentRunner(
        LazyDeepAgentRunner(
            settings,
            project_root=project_root,
            tools=tool_catalog.tools,
        ),
        max_attempts=settings.agent_max_retries,
    )
    chat_service = ChatService(
        repository=repository,
        agent_runner=agent_runner,
    )
    skills = discover_skills(project_root, settings.skills_dir) if settings.skills_enabled else []
    return AppRuntime(
        repository=repository,
        chat_service=chat_service,
        skills=skills,
        tool_catalog=tool_catalog,
    )
