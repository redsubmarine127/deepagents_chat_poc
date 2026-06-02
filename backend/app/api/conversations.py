from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.chat.schemas import SendMessageRequest, conversation_response, message_response
from app.chat.service import ChatService
from app.chat.sse import format_sse
from app.storage.conversations import InMemoryConversationRepository, UnknownConversationError


def create_router(repository: InMemoryConversationRepository, chat_service: ChatService) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/conversations")
    def list_conversations():
        return [conversation_response(item) for item in repository.list_conversations()]

    @router.post("/conversations")
    def create_conversation():
        return conversation_response(repository.create_conversation())

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(conversation_id: str):
        try:
            return [message_response(item) for item in repository.get_messages(conversation_id)]
        except UnknownConversationError as exc:
            raise HTTPException(status_code=404, detail="Conversation not found.") from exc

    @router.post("/conversations/{conversation_id}/messages/stream")
    async def stream_message(conversation_id: str, request: SendMessageRequest):
        async def event_stream():
            try:
                async for event in chat_service.stream_user_message(conversation_id, request.content):
                    yield format_sse(event)
            except UnknownConversationError:
                yield format_sse({"type": "failed", "messageId": "", "content": "Conversation not found."})
            except ValueError as exc:
                yield format_sse({"type": "failed", "messageId": "", "content": str(exc)})

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return router
