from pathlib import Path

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful intelligent conversation assistant. "
    "Answer clearly and concisely. Use Chinese when the user writes Chinese, "
    "and English when the user writes English."
)


def load_system_prompt(project_root: Path | str, prompt_path: str) -> str:
    root = Path(project_root).resolve()
    source = Path(prompt_path)
    resolved = source.resolve() if source.is_absolute() else (root / source).resolve()
    if not resolved.exists() or not resolved.is_file():
        return DEFAULT_SYSTEM_PROMPT

    content = resolved.read_text(encoding="utf-8").strip()
    return content or DEFAULT_SYSTEM_PROMPT
