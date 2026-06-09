from fastapi import APIRouter

from app.api import conversations, health, skills as skills_api, tools as tools_api
from app.chat.service import ChatService
from app.skills.schemas import SkillMetadata
from app.storage.conversations import InMemoryConversationRepository
from app.tools.schemas import ToolMetadata


def create_api_router(
    repository: InMemoryConversationRepository,
    chat_service: ChatService,
    skills: list[SkillMetadata],
    tools: list[ToolMetadata],
) -> APIRouter:
    router = APIRouter(prefix="/api")
    router.include_router(health.router)
    router.include_router(conversations.create_router(repository, chat_service))
    router.include_router(skills_api.create_router(skills))
    router.include_router(tools_api.create_router(tools))
    return router
