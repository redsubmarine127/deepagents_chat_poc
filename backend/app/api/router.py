from fastapi import APIRouter

from app.api import conversations, health, skills as skills_api
from app.chat.service import ChatService
from app.skills.schemas import SkillMetadata
from app.storage.conversations import InMemoryConversationRepository


def create_api_router(
    repository: InMemoryConversationRepository,
    chat_service: ChatService,
    skills: list[SkillMetadata],
) -> APIRouter:
    router = APIRouter(prefix="/api")
    router.include_router(health.router)
    router.include_router(conversations.create_router(repository, chat_service))
    router.include_router(skills_api.create_router(skills))
    return router
