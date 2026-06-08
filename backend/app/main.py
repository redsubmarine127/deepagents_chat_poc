from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import create_api_router
from app.chat.agent import LazyDeepAgentRunner
from app.chat.retry import RetryingAgentRunner
from app.chat.service import ChatService
from app.config import get_settings
from app.human_loop.config import build_interrupt_on
from app.human_loop.store import InMemoryApprovalStore
from app.observability import configure_app_logging
from app.skills.loader import discover_skills
from app.storage.conversations import InMemoryConversationRepository
from app.tools.loader import discover_tools, load_tools

PROJECT_ROOT = Path(__file__).resolve().parents[2]
configure_app_logging()

settings = get_settings()
repository = InMemoryConversationRepository()
approval_store = InMemoryApprovalStore()
loaded_tools = load_tools(PROJECT_ROOT, settings.tools_dir) if settings.tools_enabled else []
tool_metadata = discover_tools(PROJECT_ROOT, settings.tools_dir) if settings.tools_enabled else []
agent_runner = RetryingAgentRunner(
    LazyDeepAgentRunner(
        settings,
        tools=loaded_tools,
        interrupt_on=build_interrupt_on(),
    ),
    max_attempts=settings.agent_max_retries,
)
chat_service = ChatService(repository=repository, agent_runner=agent_runner)
skills = discover_skills(PROJECT_ROOT, settings.skills_dir) if settings.skills_enabled else []

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_api_router(repository, chat_service, skills, tool_metadata, approval_store))
