import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.errors import conversation_not_found
from app.chat.schemas import ChatMessageRequest, StreamFlag, to_conversation_response, to_message_response
from app.chat.service import ChatService
from app.chat.events import ChatApiEventFormatter, to_chat_api_response
from app.chat.sse import format_sse
from app.observability import summarize_text
from app.storage.conversations import ConversationBusyError, InMemoryConversationRepository, UnknownConversationError

logger = logging.getLogger(__name__)


def create_router(repository: InMemoryConversationRepository, chat_service: ChatService) -> APIRouter:
    router = APIRouter()

    @router.get("/conversations")
    def list_conversations():
        return [to_conversation_response(conversation) for conversation in repository.list_conversations()]

    @router.get("/conversations/{conversation_id}/messages")
    def list_messages(conversation_id: str):
        try:
            return [to_message_response(message) for message in repository.get_messages(conversation_id)]
        except UnknownConversationError as exc:
            raise conversation_not_found() from exc

    @router.post("/conversations/messages")
    async def send_message(request: ChatMessageRequest):
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Message query is required.")

        conversation = repository.ensure_conversation(request.sessionId)
        logger.info(
            "chat.request.accepted session_id=%s stream_flag=%s request_message_id=%s global_user_id=%s account=%s query_preview=%s",
            conversation.id,
            request.streamFlag,
            request.messageId,
            request.globalUserId,
            request.userAccount,
            summarize_text(query),
        )

        try:
            if request.streamFlag == StreamFlag.NON_STREAM:
                result = await chat_service.complete_user_message(conversation.id, query)
                api_response = to_chat_api_response(
                    session_id=conversation.id,
                    request_message_id=request.messageId,
                    content=result.get("content", ""),
                    status=str(result.get("status", "")),
                )
                if request.payload:
                    api_response["payload"] = request.payload
                return api_response

            event_stream = chat_service.stream_user_message(conversation.id, query)
        except UnknownConversationError as exc:
            raise conversation_not_found() from exc
        except ConversationBusyError as exc:
            raise HTTPException(status_code=409, detail="Conversation already has an active assistant turn.") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        async def message_event_stream():
            formatter = ChatApiEventFormatter(
                session_id=conversation.id,
                request_message_id=request.messageId,
            )
            async for chat_event in event_stream:
                for api_event in formatter.format(chat_event):
                    yield format_sse(api_event)

        return StreamingResponse(message_event_stream(), media_type="text/event-stream")

    return router
