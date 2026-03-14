from __future__ import annotations

from process_inspector.appcontrol.application.dtos import AppInfoDTO


def to_app_info_dto(data: dict[str, object]) -> AppInfoDTO:
    return AppInfoDTO(
        exe=data["exe"],
        name=data["name"],
        path=data["path"],
        is_installed=data["is_installed"],
        version=data["version"],
        install_date_short=data["install_date_short"],
        install_date=data["install_date"],
    )
