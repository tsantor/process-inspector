from __future__ import annotations

from process_inspector.scriptcontrol.infrastructure.execution_service import (
    ScriptExecutionService,
)


class DummyScript:
    app_name = "dummy-script"

    def __init__(self):
        self.states = []

    def _update_running_state(self, *, is_running: bool) -> None:
        self.states.append(is_running)


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
