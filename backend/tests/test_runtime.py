from app import runtime as runtime_module
from app.config import Settings


class FakeAgentRunner:
    def __init__(self, runner, max_attempts):
        self.runner = runner
        self.max_attempts = max_attempts


class FakeLazyDeepAgentRunner:
    instances = []

    def __init__(self, settings, project_root=None, tools=None, interrupt_on=None, checkpointer=None):
        self.settings = settings
        self.project_root = project_root
        self.tools = tools
        self.interrupt_on = interrupt_on
        self.checkpointer = checkpointer
        self.instances.append(self)


def test_build_runtime_disables_human_loop_by_default(monkeypatch, tmp_path):
    FakeLazyDeepAgentRunner.instances = []
    monkeypatch.setattr(runtime_module, "LazyDeepAgentRunner", FakeLazyDeepAgentRunner)
    monkeypatch.setattr(runtime_module, "RetryingAgentRunner", FakeAgentRunner)

    runtime = runtime_module.build_runtime(Settings(TOOLS_ENABLED=False, SKILLS_ENABLED=False), tmp_path)

    assert runtime.chat_service is not None
    assert FakeLazyDeepAgentRunner.instances[0].interrupt_on is None


def test_build_runtime_enables_human_loop_from_settings(monkeypatch, tmp_path):
    FakeLazyDeepAgentRunner.instances = []
    monkeypatch.setattr(runtime_module, "LazyDeepAgentRunner", FakeLazyDeepAgentRunner)
    monkeypatch.setattr(runtime_module, "RetryingAgentRunner", FakeAgentRunner)

    runtime_module.build_runtime(
        Settings(TOOLS_ENABLED=False, SKILLS_ENABLED=False, HUMAN_LOOP_ENABLED=True),
        tmp_path,
    )

    interrupt_on = FakeLazyDeepAgentRunner.instances[0].interrupt_on
    assert set(interrupt_on.keys()) == {"write_file", "edit_file"}
