from fastapi import APIRouter

from app.api import conversations, health, human_loop, skills as skills_api, tools as tools_api
from app.chat.service import ChatService
from app.human_loop.store import InMemoryApprovalStore
from app.skills.schemas import SkillMetadata
from app.storage.conversations import InMemoryConversationRepository
from app.tools.schemas import ToolMetadata


def create_api_router(
    repository: InMemoryConversationRepository,
    chat_service: ChatService,
    skills: list[SkillMetadata],
    tools: list[ToolMetadata],
    approval_store: InMemoryApprovalStore,
) -> APIRouter:
    router = APIRouter(prefix="/api")
    router.include_router(health.router)
    router.include_router(conversations.create_router(repository, chat_service))
    router.include_router(skills_api.create_router(skills))
    router.include_router(tools_api.create_router(tools))
    router.include_router(human_loop.create_router(approval_store))
    return router
