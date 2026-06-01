from __future__ import annotations

from process_inspector.oscontrol.infrastructure.reboot_service import RebootService


def build_reboot_service() -> RebootService:
    return RebootService()
