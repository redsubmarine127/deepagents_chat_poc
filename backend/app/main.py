from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import create_api_router
from app.chat.agent import LazyDeepAgentRunner
from app.chat.service import ChatService
from app.config import get_settings
from app.observability import configure_app_logging
from app.skills.loader import discover_skills
from app.storage.conversations import InMemoryConversationRepository

PROJECT_ROOT = Path(__file__).resolve().parents[2]
configure_app_logging()

settings = get_settings()
repository = InMemoryConversationRepository()
agent_runner = LazyDeepAgentRunner(settings)
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
app.include_router(create_api_router(repository, chat_service, skills))
