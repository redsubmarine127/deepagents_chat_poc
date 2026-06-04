from app.chat import agent as agent_module
from app.chat.agent import DeepAgentRunner
from app.config import Settings


class FakeChatOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeEventAgent:
    async def astream_events(self, payload, version):
        yield {
            "event": "on_tool_start",
            "name": "write_todos",
            "data": {"input": {"todos": [{"content": "Plan task", "status": "pending"}]}},
        }
        yield {
            "event": "on_tool_end",
            "name": "write_todos",
            "data": {"output": "Todo list updated"},
        }
        yield {
            "event": "on_chat_model_stream",
            "data": {"chunk": type("Chunk", (), {"content": "done"})()},
        }


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


def test_deep_agent_runner_uses_configured_system_prompt(monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompts" / "system.md"
    prompt_file.parent.mkdir()
    prompt_file.write_text("Custom prompt from disk", encoding="utf-8")
    captured = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(agent_module, "ChatOpenAI", FakeChatOpenAI)
    monkeypatch.setattr(agent_module, "create_deep_agent", fake_create_deep_agent)

    settings = Settings(
        MODEL_API_KEY="test-key",
        SKILLS_ENABLED=False,
        SYSTEM_PROMPT_PATH="prompts/system.md",
    )
    DeepAgentRunner(settings, project_root=tmp_path)

    assert captured["system_prompt"] == "Custom prompt from disk"


async def test_deep_agent_runner_converts_todo_events_to_reasoning(monkeypatch, tmp_path, caplog):
    def fake_create_deep_agent(**kwargs):
        return FakeEventAgent()

    monkeypatch.setattr(agent_module, "ChatOpenAI", FakeChatOpenAI)
    monkeypatch.setattr(agent_module, "create_deep_agent", fake_create_deep_agent)

    settings = Settings(MODEL_API_KEY="test-key", SKILLS_ENABLED=False)
    runner = DeepAgentRunner(settings, project_root=tmp_path)

    events = []
    async for event in runner.stream([{"role": "user", "content": "hi"}]):
        events.append(event)

    assert events[0]["type"] == "reasoning"
    assert "TodoList" in events[0]["content"]
    assert events[-1] == {"type": "delta", "content": "done"}
