from collections.abc import AsyncIterator

from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

from app.config import Settings

SYSTEM_PROMPT = (
    "You are a helpful intelligent conversation assistant. "
    "Answer clearly and concisely. Use Chinese when the user writes Chinese, "
    "and English when the user writes English."
)


class DeepAgentRunner:
    def __init__(self, settings: Settings) -> None:
        if not settings.model_api_key:
            raise ValueError("MODEL_API_KEY is required for remote model streaming.")

        model = ChatOpenAI(
            model=settings.model_id,
            base_url=settings.model_base_url,
            api_key=settings.model_api_key,
            temperature=settings.model_temperature,
            streaming=True,
        )
        self._agent = create_deep_agent(model=model, tools=[], system_prompt=SYSTEM_PROMPT)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        async for event in self._agent.astream_events({"messages": messages}, version="v2"):
            if event.get("event") != "on_chat_model_stream":
                continue

            chunk = event.get("data", {}).get("chunk")
            content = getattr(chunk, "content", "")
            if isinstance(content, str) and content:
                yield content


class LazyDeepAgentRunner:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._runner: DeepAgentRunner | None = None

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        if self._runner is None:
            self._runner = DeepAgentRunner(self._settings)
        async for chunk in self._runner.stream(messages):
            yield chunk
