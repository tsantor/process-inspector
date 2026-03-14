from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def read_text_file(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf8").strip()
    return ""
