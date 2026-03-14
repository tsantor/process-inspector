from __future__ import annotations

from process_inspector.scriptcontrol.application.service import ScriptExecutionService


def build_script_execution_service() -> ScriptExecutionService:
    return ScriptExecutionService()
