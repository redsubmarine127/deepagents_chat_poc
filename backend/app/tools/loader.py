from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Any

from app.tools.schemas import ToolMetadata

logger = logging.getLogger(__name__)


def discover_tools(root_dir: Path | str, tools_dir: str) -> list[ToolMetadata]:
    root = Path(root_dir).resolve()
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


def load_tools(root_dir: Path | str, tools_dir: str) -> list[Any]:
    root = Path(root_dir).resolve()
    loaded_tools: list[Any] = []
    for metadata in discover_tools(root, tools_dir):
        tool_dir = root / Path(metadata.path).parent
        tool_file = tool_dir / "tool.py"
        try:
            loaded_tool = _load_tool_from_file(tool_file, metadata.id)
        except Exception as exc:
            logger.warning("tools.skip id=%s path=%s error=%s", metadata.id, tool_file, exc)
            continue
        loaded_tools.append(loaded_tool)
    logger.info("tools.loaded count=%d", len(loaded_tools))
    return loaded_tools


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
    lines = metadata_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator:
            metadata[key.strip()] = value.strip().strip("\"'")
    return metadata
