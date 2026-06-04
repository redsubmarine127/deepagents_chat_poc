from app.chat import agent as agent_module
from app.chat.agent import DeepAgentRunner
from app.config import Settings


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_deep_agent_runner_enables_skills_when_directory_exists(monkeypatch, tmp_path):
    (tmp_path / "skills").mkdir()
    captured = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(agent_module, "ChatOpenAI", FakeChatOpenAI)
    monkeypatch.setattr(agent_module, "create_deep_agent", fake_create_deep_agent)

    settings = Settings(MODEL_API_KEY="test-key", SKILLS_ENABLED=True, SKILLS_DIR="skills")
    DeepAgentRunner(settings, project_root=tmp_path)

    assert captured["skills"] == ["/skills/"]
    assert captured["backend"].cwd == tmp_path.resolve()
    assert [rule.mode for rule in captured["permissions"]] == ["allow", "deny", "deny"]


def test_deep_agent_runner_skips_skills_when_disabled(monkeypatch, tmp_path):
    (tmp_path / "skills").mkdir()
    captured = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(agent_module, "ChatOpenAI", FakeChatOpenAI)
    monkeypatch.setattr(agent_module, "create_deep_agent", fake_create_deep_agent)

    settings = Settings(MODEL_API_KEY="test-key", SKILLS_ENABLED=False, SKILLS_DIR="skills")
    DeepAgentRunner(settings, project_root=tmp_path)

    assert captured["skills"] is None
    assert captured["backend"] is None
    assert captured["permissions"] is None
