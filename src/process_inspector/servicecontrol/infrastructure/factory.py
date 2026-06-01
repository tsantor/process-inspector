from __future__ import annotations

from process_inspector.servicecontrol.infrastructure.repository import (
    PsutilServiceRuntimeRepository,
)
from process_inspector.servicecontrol.infrastructure.runtime_service import (
    ServiceRuntimeService,
)


def build_runtime_service(state_change_callback=None) -> ServiceRuntimeService:
    return ServiceRuntimeService(
        runtime_port=PsutilServiceRuntimeRepository(),
        state_change_callback=state_change_callback,
    )
