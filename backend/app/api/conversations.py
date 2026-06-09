from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.errors import conversation_not_found
from app.chat.schemas import SendMessageRequest, to_conversation_response, to_message_response
from app.chat.service import ChatService
from app.chat.sse import format_sse
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository, UnknownConversationError


def create_router(repository: InMemoryConversationRepository, chat_service: ChatService) -> APIRouter:
    router = APIRouter()

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
            raise conversation_not_found() from exc

    @router.post("/conversations/{conversation_id}/messages/stream")
    async def stream_message(conversation_id: str, request: SendMessageRequest):
        try:
            event_stream = chat_service.stream_user_message(conversation_id, request.content)
        except UnknownConversationError as exc:
            raise conversation_not_found() from exc
        except ConversationBusyError as exc:
            raise HTTPException(status_code=409, detail="Conversation already has an active assistant turn.") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        async def message_event_stream():
            async for chat_event in event_stream:
                yield format_sse(chat_event)

        return StreamingResponse(message_event_stream(), media_type="text/event-stream")

    return router
