from __future__ import annotations

from process_inspector.oscontrol.application.service import RebootService
from process_inspector.oscontrol.infrastructure.repository import (
    SubprocessCommandRunner,
)


def build_reboot_service() -> RebootService:
    return RebootService(command_runner=SubprocessCommandRunner())
