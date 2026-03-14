from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppInfoDTO:
    exe: str
    name: str
    path: str
    is_installed: bool
    version: str
    install_date_short: str | None
    install_date: str | None

    def as_dict(self) -> dict:
        return {
            "exe": self.exe,
            "name": self.name,
            "path": self.path,
            "is_installed": self.is_installed,
            "version": self.version,
            "install_date_short": self.install_date_short,
            "install_date": self.install_date,
        }


@dataclass(frozen=True, slots=True)
class ProcessInfoDTO:
    data: dict

    def as_dict(self) -> dict:
        return dict(self.data)
