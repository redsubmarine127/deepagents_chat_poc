from pathlib import Path

from app.skills.schemas import SkillMetadata


def discover_skills(root_dir: Path | str, skills_dir: str) -> list[SkillMetadata]:
    root = Path(root_dir).resolve()
    source = _resolve_source(root, skills_dir)
    if not source.exists() or not source.is_dir():
        return []

    skills: list[SkillMetadata] = []
    for skill_file in sorted(source.rglob("SKILL.md")):
        metadata = _read_metadata(skill_file)
        skill_id = metadata.get("name") or skill_file.parent.name
        skills.append(
            SkillMetadata(
                id=skill_id,
                name=metadata.get("name") or skill_id,
                description=metadata.get("description", ""),
                path=skill_file.relative_to(root).as_posix(),
            )
        )
    return skills


def _resolve_source(root: Path, skills_dir: str) -> Path:
    source = Path(skills_dir)
    if source.is_absolute():
        return source.resolve()
    return (root / source).resolve()


def _read_metadata(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
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
