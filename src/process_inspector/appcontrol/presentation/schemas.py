from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppInfoSchema:
    data: dict


@dataclass(frozen=True, slots=True)
class ProcessInfoSchema:
    data: dict
