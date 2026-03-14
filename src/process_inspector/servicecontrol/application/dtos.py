from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ServiceInfoDTO:
    name: str

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name}


@dataclass(frozen=True, slots=True)
class ServiceProcessInfoDTO:
    data: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return dict(self.data)
