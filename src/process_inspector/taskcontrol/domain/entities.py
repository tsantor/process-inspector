from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TaskSnapshot:
    data: dict | None = None
