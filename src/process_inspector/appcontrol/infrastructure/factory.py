from __future__ import annotations

from process_inspector.appcontrol.infrastructure.repository import (
    PsutilRuntimeRepository,
)
from process_inspector.appcontrol.infrastructure.runtime_service import (
    AppRuntimeService,
)


def build_runtime_service(state_change_callback=None) -> AppRuntimeService:
    return AppRuntimeService(
        runtime_port=PsutilRuntimeRepository(),
        state_change_callback=state_change_callback,
    )
