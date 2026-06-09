from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import logging
from pathlib import Path
from typing import Any

from app.metadata.frontmatter import read_frontmatter
from app.tools.schemas import ToolMetadata

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolCatalog:
    metadata: list[ToolMetadata]
    tools: list[Any]


def discover_tools(root_dir: Path | str, tools_dir: str) -> list[ToolMetadata]:
    return _discover_tool_metadata(Path(root_dir).resolve(), tools_dir)


def load_tools(root_dir: Path | str, tools_dir: str) -> list[Any]:
    return load_tool_catalog(root_dir, tools_dir).tools


def load_tool_catalog(root_dir: Path | str, tools_dir: str) -> ToolCatalog:
    root = Path(root_dir).resolve()
    metadata = _discover_tool_metadata(root, tools_dir)
    metadata_by_id = {tool.id: tool for tool in metadata}
    loaded_tools: list[Any] = []
    for tool_metadata in metadata:
        tool_dir = root / Path(tool_metadata.path).parent
        tool_file = tool_dir / "tool.py"
        try:
            loaded_tool = _load_tool_from_file(tool_file, tool_metadata.id)
        except Exception as exc:
            load_error = _bounded_error(exc)
            metadata_by_id[tool_metadata.id] = tool_metadata.model_copy(
                update={"available": False, "loadError": load_error}
            )
            logger.warning("tools.skip id=%s path=%s error=%s", tool_metadata.id, tool_file, exc)
            continue
        loaded_tools.append(loaded_tool)
    logger.info("tools.loaded count=%d", len(loaded_tools))
    return ToolCatalog(metadata=[metadata_by_id[tool.id] for tool in metadata], tools=loaded_tools)


def empty_tool_catalog() -> ToolCatalog:
    return ToolCatalog(metadata=[], tools=[])


def _discover_tool_metadata(root: Path, tools_dir: str) -> list[ToolMetadata]:
    source_dir = _resolve_tools_dir(root, tools_dir)
    logger.info("tools.resolve configured_dir=%s source_dir=%s", tools_dir, source_dir)
    if not source_dir.exists() or not source_dir.is_dir():
        logger.info("tools.missing source_dir=%s", source_dir)
        return []

    tools: list[ToolMetadata] = []
    for metadata_file in sorted(source_dir.rglob("TOOL.md")):
        try:
            metadata = _read_metadata(metadata_file)
        except OSError as exc:
            logger.warning("tools.skip path=%s error=%s", metadata_file, exc)
            continue
        tool_id = metadata.get("name") or metadata_file.parent.name
        tools.append(
            ToolMetadata(
                id=tool_id,
                name=metadata.get("name") or tool_id,
                description=metadata.get("description", ""),
                path=metadata_file.relative_to(root).as_posix(),
            )
        )
    logger.info("tools.discovered source_dir=%s count=%d tool_ids=%s", source_dir, len(tools), [tool.id for tool in tools])
    return tools


def _resolve_tools_dir(root: Path, tools_dir: str) -> Path:
    configured = Path(tools_dir)
    if not str(tools_dir).strip():
        return root / "__missing_tools__"
    return configured.resolve() if configured.is_absolute() else (root / configured).resolve()


def _load_tool_from_file(tool_file: Path, tool_id: str) -> Any:
    if not tool_file.exists() or not tool_file.is_file():
        raise FileNotFoundError(f"Tool module not found for {tool_id}: {tool_file}")
    module_name = f"app_loaded_tool_{tool_id.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, tool_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to import tool module: {tool_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    get_tool = getattr(module, "get_tool", None)
    if not callable(get_tool):
        raise AttributeError(f"Tool module must define get_tool(): {tool_file}")
    return get_tool()


def _read_metadata(metadata_file: Path) -> dict[str, str]:
    return read_frontmatter(metadata_file)


def _bounded_error(exc: Exception, limit: int = 300) -> str:
    text = str(exc)
    return text if len(text) <= limit else f"{text[:limit]}..."
