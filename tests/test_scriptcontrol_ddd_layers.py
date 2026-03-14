from __future__ import annotations

from pathlib import Path

from process_inspector.scriptcontrol.application.service import ScriptExecutionService
from process_inspector.scriptcontrol.domain.entities import ScriptExecution
from process_inspector.scriptcontrol.domain.value_objects import ScriptIdentity
from process_inspector.scriptcontrol.infrastructure.repository import (
    LocalScriptRepository,
)


class DummyScript:
    app_name = "dummy-script"

    def __init__(self):
        self.states = []

    def _update_running_state(self, *, is_running: bool) -> None:
        self.states.append(is_running)


def test_script_identity_name():
    identity = ScriptIdentity(name="job")
    assert identity.name == "job"


def test_script_execution_entity():
    elapsed = 0.1
    execution = ScriptExecution(succeeded=True, elapsed_seconds=elapsed)
    assert execution.succeeded is True
    assert execution.elapsed_seconds == elapsed


def test_script_execution_service_success_updates_state():
    script = DummyScript()
    service = ScriptExecutionService()

    def set_running_state(*, is_running: bool) -> None:
        script.states.append(is_running)

    result = service.run(
        script,
        run_callable=lambda: True,
        set_running_state=set_running_state,
    )

    assert result is True
    assert script.states == [True, False]


def test_repository_passthrough():
    repo = LocalScriptRepository()
    result = repo.run_script(Path("script.sh"), lambda _: True)
    assert result is True
