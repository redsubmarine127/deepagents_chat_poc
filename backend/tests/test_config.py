from app.config import Settings


def test_settings_reads_app_name_environment(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Custom Chat")

    settings = Settings()

    assert settings.app_name == "Custom Chat"


def test_settings_reads_model_environment(monkeypatch):
    monkeypatch.setenv("MODEL_ID", "test-model")
    monkeypatch.setenv("MODEL_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("MODEL_API_KEY", "test-key")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.2")
    monkeypatch.setenv("CORS_ORIGINS", "http://127.0.0.1:5173")

    settings = Settings()

    assert settings.model_id == "test-model"
    assert settings.model_base_url == "https://example.test/v1"
    assert settings.model_api_key == "test-key"
    assert settings.model_temperature == 0.2
    assert settings.cors_origins == ["http://127.0.0.1:5173"]


def test_settings_parses_comma_separated_cors(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test,http://b.test")

    settings = Settings()

    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_settings_reads_skill_loading_environment(monkeypatch):
    monkeypatch.setenv("SKILLS_ENABLED", "false")
    monkeypatch.setenv("SKILLS_DIR", "custom-skills")

    settings = Settings()

    assert settings.skills_enabled is False
    assert settings.skills_dir == "custom-skills"


def test_settings_reads_system_prompt_path(monkeypatch):
    monkeypatch.setenv("SYSTEM_PROMPT_PATH", "custom/prompts/system.md")

    settings = Settings()

    assert settings.system_prompt_path == "custom/prompts/system.md"


def test_settings_reads_agent_max_retries(monkeypatch):
    monkeypatch.setenv("AGENT_MAX_RETRIES", "5")

    settings = Settings()

    assert settings.agent_max_retries == 5


def test_settings_reads_tool_loading_environment(monkeypatch):
    monkeypatch.setenv("TOOLS_ENABLED", "false")
    monkeypatch.setenv("TOOLS_DIR", "custom-tools")

    settings = Settings()

    assert settings.tools_enabled is False
    assert settings.tools_dir == "custom-tools"
