from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class LocalScriptRepository:
    def run_script(self, path: Path, run_callable) -> bool:
        return run_callable(path)
