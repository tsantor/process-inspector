from __future__ import annotations

from process_inspector.scriptcontrol.infrastructure.factory import (
    build_script_execution_service,
)


def get_script_execution_service():
    return build_script_execution_service()
