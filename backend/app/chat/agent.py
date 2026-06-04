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
from app.chat.prompts import load_system_prompt

logger = logging.getLogger(__name__)


class DeepAgentRunner:
    def __init__(self, settings: Settings, project_root: Path | None = None) -> None:
        if not settings.model_api_key:
            raise ValueError("MODEL_API_KEY is required for remote model streaming.")

        root = project_root or Path(__file__).resolve().parents[3]
        system_prompt = load_system_prompt(root, settings.system_prompt_path)
        skills, backend, permissions = _resolve_deepagents_skills(settings, root)
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

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[dict[str, str]]:
        async for event in self._agent.astream_events({"messages": messages}, version="v2"):
            stream_event = _map_deepagents_event(event)
            if stream_event is None:
                continue

            yield stream_event


class LazyDeepAgentRunner:
    def __init__(self, settings: Settings, project_root: Path | None = None) -> None:
        self._settings = settings
        self._project_root = project_root
        self._runner: DeepAgentRunner | None = None

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[dict[str, str]]:
        if self._runner is None:
            self._runner = DeepAgentRunner(self._settings, project_root=self._project_root)
        async for chunk in self._runner.stream(messages):
            yield chunk


def _map_deepagents_event(event: dict[str, Any]) -> dict[str, str] | None:
    event_name = event.get("event")
    tool_name = event.get("name", "")
    data = event.get("data", {})

    if event_name == "on_chat_model_stream":
        chunk = data.get("chunk")
        content = getattr(chunk, "content", "")
        if isinstance(content, str) and content:
            return {"type": "delta", "content": content}
        return None

    if event_name == "on_tool_start":
        if tool_name == "write_todos":
            content = _format_todo_payload("TodoList 更新中", data.get("input"))
            logger.info("TodoList update start: %s", _safe_json(data.get("input")))
            return {"type": "reasoning", "content": content}
        if tool_name == "read_file":
            return {"type": "reasoning", "content": _format_read_file_event(data.get("input"))}
        if tool_name:
            return {"type": "reasoning", "content": f"调用工具：{tool_name}"}

    if event_name == "on_tool_end" and tool_name == "write_todos":
        content = _format_todo_payload("TodoList 已更新", data.get("output"))
        logger.info("TodoList update end: %s", _safe_json(data.get("output")))
        return {"type": "reasoning", "content": content}

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
        return None, None, None

    source = Path(settings.skills_dir)
    if source.is_absolute():
        root = source.parent.resolve()
        skill_source = f"/{source.name}/"
    else:
        root = project_root.resolve()
        resolved_source = (root / source).resolve()
        if not resolved_source.exists() or not resolved_source.is_dir():
            return None, None, None
        skill_source = f"/{source.as_posix().strip('/')}/"

    if not (root / skill_source.strip("/")).exists():
        return None, None, None

    permissions = [
        FilesystemPermission(operations=["read"], paths=[f"{skill_source}**"], mode="allow"),
        FilesystemPermission(operations=["read"], paths=["/**"], mode="deny"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]
    return [skill_source], FilesystemBackend(root_dir=root, virtual_mode=True), permissions
