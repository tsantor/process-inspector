from __future__ import annotations

from process_inspector.servicecontrol.infrastructure.factory import (
    build_runtime_service,
)


def get_runtime_service(state_change_callback=None):
    return build_runtime_service(state_change_callback=state_change_callback)
