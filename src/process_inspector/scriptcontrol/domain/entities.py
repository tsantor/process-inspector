from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScriptExecution:
    succeeded: bool
    elapsed_seconds: float
