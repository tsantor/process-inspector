from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceInfoSchema:
    data: dict


@dataclass(frozen=True, slots=True)
class ServiceProcessInfoSchema:
    data: dict
