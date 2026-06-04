from collections.abc import AsyncIterator
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemPermission
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.chat.prompts import load_system_prompt


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

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        async for event in self._agent.astream_events({"messages": messages}, version="v2"):
            if event.get("event") != "on_chat_model_stream":
                continue

            chunk = event.get("data", {}).get("chunk")
            content = getattr(chunk, "content", "")
            if isinstance(content, str) and content:
                yield content


class LazyDeepAgentRunner:
    def __init__(self, settings: Settings, project_root: Path | None = None) -> None:
        self._settings = settings
        self._project_root = project_root
        self._runner: DeepAgentRunner | None = None

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        if self._runner is None:
            self._runner = DeepAgentRunner(self._settings, project_root=self._project_root)
        async for chunk in self._runner.stream(messages):
            yield chunk


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
