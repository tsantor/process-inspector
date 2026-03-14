from __future__ import annotations

from process_inspector.servicecontrol.application.service import ServiceRuntimeService
from process_inspector.servicecontrol.infrastructure.repository import (
    PsutilServiceRuntimeRepository,
)


def build_runtime_service(state_change_callback=None) -> ServiceRuntimeService:
    return ServiceRuntimeService(
        runtime_port=PsutilServiceRuntimeRepository(),
        state_change_callback=state_change_callback,
    )
