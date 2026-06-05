import logging

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


def test_discover_skills_logs_resolution_and_count(tmp_path, caplog):
    skill_file = tmp_path / "skills" / "requirements" / "SKILL.md"
    skill_file.parent.mkdir(parents=True)
    skill_file.write_text("---\nname: requirements\n---\n", encoding="utf-8")

    caplog.set_level(logging.INFO, logger="app.skills.loader")

    discover_skills(tmp_path, "skills")

    log_text = "\n".join(record.getMessage() for record in caplog.records)
    assert "skills.resolve" in log_text
    assert "skills.discovered" in log_text
    assert "count=1" in log_text


def test_discover_skills_skips_bad_skill_file(tmp_path, monkeypatch, caplog):
    valid_skill = tmp_path / "skills" / "valid" / "SKILL.md"
    bad_skill = tmp_path / "skills" / "bad" / "SKILL.md"
    valid_skill.parent.mkdir(parents=True)
    bad_skill.parent.mkdir(parents=True)
    valid_skill.write_text("---\nname: valid\n---\n", encoding="utf-8")
    bad_skill.write_text("---\nname: bad\n---\n", encoding="utf-8")

    original_read_text = type(bad_skill).read_text

    def read_text_with_bad_file(path, *args, **kwargs):
        if path == bad_skill:
            raise OSError("cannot read")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(type(bad_skill), "read_text", read_text_with_bad_file)
    caplog.set_level(logging.WARNING, logger="app.skills.loader")

    skills = discover_skills(tmp_path, "skills")

    assert [skill.id for skill in skills] == ["valid"]
    assert "skills.skip" in "\n".join(record.getMessage() for record in caplog.records)
