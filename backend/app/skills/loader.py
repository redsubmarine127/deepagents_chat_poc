from dataclasses import dataclass
import logging
from pathlib import Path

from app.skills.schemas import SkillMetadata

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SkillDirectory:
    root_dir: Path
    source_dir: Path
    virtual_path: str


def resolve_skill_directory(root_dir: Path | str, skills_dir: str) -> SkillDirectory:
    configured_dir = Path(skills_dir)
    if not str(skills_dir).strip():
        root = Path(root_dir).resolve()
        skill_directory = SkillDirectory(
            root_dir=root,
            source_dir=root / "__missing_skills__",
            virtual_path="/__missing_skills__/",
        )
        logger.info(
            "skills.resolve configured_dir=%s root_dir=%s source_dir=%s virtual_path=%s",
            skills_dir,
            skill_directory.root_dir,
            skill_directory.source_dir,
            skill_directory.virtual_path,
        )
        return skill_directory

    if configured_dir.is_absolute():
        # DeepAgents exposes files through a virtual root, so an absolute skills path becomes /<dir-name>/.
        root = configured_dir.parent.resolve()
        virtual_path = f"/{configured_dir.name}/"
        skill_directory = SkillDirectory(root_dir=root, source_dir=root / configured_dir.name, virtual_path=virtual_path)
        logger.info(
            "skills.resolve configured_dir=%s root_dir=%s source_dir=%s virtual_path=%s",
            configured_dir,
            skill_directory.root_dir,
            skill_directory.source_dir,
            skill_directory.virtual_path,
        )
        return skill_directory

    root = Path(root_dir).resolve()
    relative_path = configured_dir.as_posix().strip("/")
    virtual_path = f"/{relative_path}/"
    skill_directory = SkillDirectory(root_dir=root, source_dir=(root / configured_dir).resolve(), virtual_path=virtual_path)
    logger.info(
        "skills.resolve configured_dir=%s root_dir=%s source_dir=%s virtual_path=%s",
        configured_dir,
        skill_directory.root_dir,
        skill_directory.source_dir,
        skill_directory.virtual_path,
    )
    return skill_directory


def discover_skills(root_dir: Path | str, skills_dir: str) -> list[SkillMetadata]:
    skill_directory = resolve_skill_directory(root_dir, skills_dir)
    if not skill_directory.source_dir.exists() or not skill_directory.source_dir.is_dir():
        logger.info("skills.missing source_dir=%s", skill_directory.source_dir)
        return []

    skills: list[SkillMetadata] = []
    for skill_file in sorted(skill_directory.source_dir.rglob("SKILL.md")):
        try:
            metadata = _read_metadata(skill_file)
        except OSError as exc:
            logger.warning("skills.skip path=%s error=%s", skill_file, exc)
            continue
        skill_id = metadata.get("name") or skill_file.parent.name
        skills.append(
            SkillMetadata(
                id=skill_id,
                name=metadata.get("name") or skill_id,
                description=metadata.get("description", ""),
                path=skill_file.relative_to(skill_directory.root_dir).as_posix(),
            )
        )
    logger.info(
        "skills.discovered source_dir=%s count=%d skill_ids=%s",
        skill_directory.source_dir,
        len(skills),
        [skill.id for skill in skills],
    )
    return skills


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
