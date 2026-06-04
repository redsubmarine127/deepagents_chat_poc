from app.chat.prompts import DEFAULT_SYSTEM_PROMPT, load_system_prompt


def test_load_system_prompt_reads_configured_file(tmp_path):
    prompt_file = tmp_path / "prompts" / "system.md"
    prompt_file.parent.mkdir()
    prompt_file.write_text("Custom system prompt\n", encoding="utf-8")

    prompt = load_system_prompt(tmp_path, "prompts/system.md")

    assert prompt == "Custom system prompt"


def test_load_system_prompt_falls_back_when_file_missing(tmp_path):
    prompt = load_system_prompt(tmp_path, "prompts/system.md")

    assert prompt == DEFAULT_SYSTEM_PROMPT


def test_load_system_prompt_falls_back_when_file_empty(tmp_path):
    prompt_file = tmp_path / "prompts" / "system.md"
    prompt_file.parent.mkdir()
    prompt_file.write_text("  \n", encoding="utf-8")

    prompt = load_system_prompt(tmp_path, "prompts/system.md")

    assert prompt == DEFAULT_SYSTEM_PROMPT
