from __future__ import annotations

from process_inspector.oscontrol.infrastructure.factory import build_reboot_service


def get_reboot_service():
    return build_reboot_service()
