from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.conversations import create_router as create_conversations_router
from app.api.health import router as health_router
from app.chat.agent import LazyDeepAgentRunner
from app.chat.service import ChatService
from app.config import get_settings
from app.storage.conversations import InMemoryConversationRepository

settings = get_settings()
repository = InMemoryConversationRepository()
agent_runner = LazyDeepAgentRunner(settings)
chat_service = ChatService(repository=repository, agent_runner=agent_runner)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(create_conversations_router(repository, chat_service))
