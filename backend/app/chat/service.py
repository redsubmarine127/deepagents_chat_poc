from collections.abc import AsyncIterator
from typing import Protocol

from app.chat.schemas import MessageRole, MessageStatus
from app.storage.conversations import InMemoryConversationRepository


class AgentRunner(Protocol):
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[dict[str, str]]:
        pass


class ChatService:
    def __init__(self, repository: InMemoryConversationRepository, agent_runner: AgentRunner) -> None:
        self._repository = repository
        self._agent_runner = agent_runner

    async def stream_user_message(self, conversation_id: str, content: str) -> AsyncIterator[dict[str, str]]:
        text = content.strip()
        if not text:
            raise ValueError("Message content is required.")

        self._repository.append_message(conversation_id, role=MessageRole.USER, content=text)
        assistant = self._repository.append_message(
            conversation_id,
            role=MessageRole.ASSISTANT,
            content="",
            status=MessageStatus.STREAMING,
        )
        yield {"type": "started", "messageId": assistant.id, "content": ""}
        yield {
            "type": "reasoning",
            "messageId": assistant.id,
            "content": "已创建任务上下文，开始调用 Agent",
        }

        chunks: list[str] = []
        history = [
            {"role": message.role.value, "content": message.content}
            for message in self._repository.get_messages(conversation_id)
            if message.id != assistant.id
        ]

        try:
            async for event in self._agent_runner.stream(history):
                event_type = event.get("type")
                content_chunk = event.get("content", "")
                if event_type == "reasoning":
                    yield {"type": "reasoning", "messageId": assistant.id, "content": content_chunk}
                    continue
                if event_type != "delta":
                    continue

                chunks.append(content_chunk)
                yield {"type": "delta", "messageId": assistant.id, "content": content_chunk}

            final_content = "".join(chunks)
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=final_content,
                status=MessageStatus.COMPLETED,
            )
            yield {"type": "completed", "messageId": assistant.id, "content": final_content}
        except Exception as exc:
            failure = f"Assistant generation failed: {exc}"
            self._repository.update_message(
                conversation_id,
                assistant.id,
                content=failure,
                status=MessageStatus.FAILED,
            )
            yield {"type": "failed", "messageId": assistant.id, "content": failure}
