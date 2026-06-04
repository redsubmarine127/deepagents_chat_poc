from collections.abc import AsyncIterator
import json
import logging
from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemPermission
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.chat.events import ChatStreamEvent, stream_delta, stream_reasoning
from app.chat.prompts import load_system_prompt
from app.observability import summarize_payload, summarize_text
from app.skills.loader import resolve_skill_directory

logger = logging.getLogger(__name__)


class DeepAgentRunner:
    def __init__(self, settings: Settings, project_root: Path | None = None) -> None:
        if not settings.model_api_key:
            raise ValueError("MODEL_API_KEY is required for remote model streaming.")

        root = project_root or Path(__file__).resolve().parents[3]
        system_prompt = load_system_prompt(root, settings.system_prompt_path)
        skills, backend, permissions = _resolve_deepagents_skills(settings, root)
        logger.info(
            "agent.init model_id=%s model_base_url=%s temperature=%s system_prompt_path=%s skills_enabled=%s skill_paths=%s",
            settings.model_id,
            settings.model_base_url,
            settings.model_temperature,
            settings.system_prompt_path,
            settings.skills_enabled,
            skills or [],
        )
        model = ChatOpenAI(
            model=settings.model_id,
            base_url=settings.model_base_url,
            api_key=settings.model_api_key,
            temperature=settings.model_temperature,
            streaming=True,
        )
        self._agent = create_deep_agent(
            model=model,
            tools=[],
            system_prompt=system_prompt,
            skills=skills,
            backend=backend,
            permissions=permissions,
        )

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[ChatStreamEvent]:
        logger.info("agent.stream.start message_count=%d", len(messages))
        async for raw_event in self._agent.astream_events({"messages": messages}, version="v2"):
            chat_event = _map_deepagents_event(raw_event)
            if chat_event is None:
                continue

            yield chat_event
        logger.info("agent.stream.end message_count=%d", len(messages))


class LazyDeepAgentRunner:
    def __init__(self, settings: Settings, project_root: Path | None = None) -> None:
        self._settings = settings
        self._project_root = project_root
        self._runner: DeepAgentRunner | None = None

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[ChatStreamEvent]:
        if self._runner is None:
            self._runner = DeepAgentRunner(self._settings, project_root=self._project_root)
        async for chat_event in self._runner.stream(messages):
            yield chat_event


def _map_deepagents_event(raw_event: dict[str, Any]) -> ChatStreamEvent | None:
    # DeepAgents emits LangChain callback events; the UI only needs answer deltas and observable tool progress.
    event_name = raw_event.get("event")
    tool_name = raw_event.get("name", "")
    event_data = raw_event.get("data", {})

    if event_name == "on_chat_model_stream":
        chunk = event_data.get("chunk")
        content = getattr(chunk, "content", "")
        if isinstance(content, str) and content:
            logger.info(
                "agent.model.delta chunk_length=%d chunk_preview=%s",
                len(content),
                summarize_text(content, limit=80),
            )
            return stream_delta(content)
        return None

    if event_name == "on_tool_start":
        if tool_name:
            logger.info(
                "agent.tool.start tool_name=%s input=%s",
                tool_name,
                summarize_payload(event_data.get("input")),
            )
        if tool_name == "write_todos":
            tool_input = event_data.get("input")
            content = _format_todo_payload("TodoList 更新中", tool_input)
            logger.info("agent.todo.start payload=%s", summarize_payload(tool_input))
            return stream_reasoning(content)
        if tool_name == "read_file":
            return stream_reasoning(_format_read_file_event(event_data.get("input")))
        if tool_name:
            return stream_reasoning(f"调用工具：{tool_name}")

    if event_name == "on_tool_end" and tool_name:
        logger.info(
            "agent.tool.end tool_name=%s output=%s",
            tool_name,
            summarize_payload(event_data.get("output")),
        )
        if tool_name != "write_todos":
            return None

        tool_output = event_data.get("output")
        content = _format_todo_payload("TodoList 已更新", tool_output)
        logger.info("agent.todo.end payload=%s", summarize_payload(tool_output))
        return stream_reasoning(content)

    return None


def _format_todo_payload(prefix: str, payload: Any) -> str:
    return f"{prefix}: {_safe_json(payload)}"


def _format_read_file_event(payload: Any) -> str:
    if isinstance(payload, dict):
        path = payload.get("file_path") or payload.get("path")
        if path:
            return f"按需读取文件：{path}"
    return "按需读取文件"


def _safe_json(payload: Any) -> str:
    try:
        return json.dumps(payload, ensure_ascii=False)
    except TypeError:
        return str(payload)


def _resolve_deepagents_skills(
    settings: Settings,
    project_root: Path,
) -> tuple[list[str] | None, FilesystemBackend | None, list[FilesystemPermission] | None]:
    if not settings.skills_enabled:
        logger.info("agent.skills.disabled")
        return None, None, None

    skill_directory = resolve_skill_directory(project_root, settings.skills_dir)
    if not skill_directory.source_dir.exists() or not skill_directory.source_dir.is_dir():
        logger.info("agent.skills.missing source_dir=%s", skill_directory.source_dir)
        return None, None, None

    permissions = [
        FilesystemPermission(operations=["read"], paths=[f"{skill_directory.virtual_path}**"], mode="allow"),
        FilesystemPermission(operations=["read"], paths=["/**"], mode="deny"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]
    backend = FilesystemBackend(root_dir=skill_directory.root_dir, virtual_mode=True)
    logger.info(
        "agent.skills.enabled root_dir=%s virtual_path=%s permissions=%d",
        skill_directory.root_dir,
        skill_directory.virtual_path,
        len(permissions),
    )
    return [skill_directory.virtual_path], backend, permissions
