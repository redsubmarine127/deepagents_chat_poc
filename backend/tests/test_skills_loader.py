from app.skills.loader import discover_skills


def test_discover_skills_reads_frontmatter_metadata(tmp_path):
    skill_file = tmp_path / "skills" / "requirements" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text(
        """---
name: requirements
description: Use when analyzing product requirements.
---

# Requirements

Detailed instructions stay on disk until needed.
""",
        encoding="utf-8",
    )

    skills = discover_skills(tmp_path, "skills")

    assert len(skills) == 1
    assert skills[0].id == "requirements"
    assert skills[0].name == "requirements"
    assert skills[0].description == "Use when analyzing product requirements."
    assert skills[0].path == "skills/requirements/SKILL.md"


def test_discover_skills_returns_empty_for_missing_directory(tmp_path):
    assert discover_skills(tmp_path, "skills") == []
