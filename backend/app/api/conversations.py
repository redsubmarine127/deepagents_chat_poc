from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.chat.events import stream_failed
from app.chat.schemas import SendMessageRequest, to_conversation_response, to_message_response
from app.chat.service import ChatService
from app.chat.sse import format_sse
from app.storage.conversations import InMemoryConversationRepository, UnknownConversationError


def create_router(repository: InMemoryConversationRepository, chat_service: ChatService) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/conversations")
    def list_conversations():
        return [to_conversation_response(conversation) for conversation in repository.list_conversations()]

    @router.post("/conversations")
    def create_conversation():
        return to_conversation_response(repository.create_conversation())

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(conversation_id: str):
        try:
            return [to_message_response(message) for message in repository.get_messages(conversation_id)]
        except UnknownConversationError as exc:
            raise HTTPException(status_code=404, detail="Conversation not found.") from exc

    @router.post("/conversations/{conversation_id}/messages/stream")
    async def stream_message(conversation_id: str, request: SendMessageRequest):
        async def event_stream():
            try:
                async for chat_event in chat_service.stream_user_message(conversation_id, request.content):
                    yield format_sse(chat_event)
            except UnknownConversationError:
                yield format_sse(stream_failed("Conversation not found."))
            except ValueError as exc:
                yield format_sse(stream_failed(str(exc)))

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return router
