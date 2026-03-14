from __future__ import annotations

from process_inspector.teamviewer.domain.value_objects import TeamviewerInfo


def to_teamviewer_info(data: dict) -> TeamviewerInfo:
    return TeamviewerInfo(
        id=str(data.get("id", "--")),
        version=str(data.get("version", "--")),
        path=str(data.get("path", "")),
        is_installed=bool(data.get("is_installed", False)),
    )
