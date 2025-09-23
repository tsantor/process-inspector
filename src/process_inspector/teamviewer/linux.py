import contextlib
import logging
import re
import shlex
import subprocess
from functools import cache
from pathlib import Path

logger = logging.getLogger(__name__)


def _extract_teamviewer_id(hex_str) -> str:
    """Extract the ID."""
    regex = r"\d{9,10}"
    matches = re.search(regex, hex_str)
    return matches[0] if matches else ""


def _query_teamviewer_id() -> str:
    """Safely get TeamViewer ID from command line."""
    with contextlib.suppress(subprocess.CalledProcessError):
        cmd = 'sudo teamviewer -info | grep "TeamViewer ID"'
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=True, capture_output=True, text=True
        )
        return proc.stdout.strip()
    return "--"


def _extract_teamviewer_version(hex_str) -> str:
    """Extract the version."""
    regex = r"\d{2}\.\d{2}\.\d{1,2}"
    matches = re.search(regex, hex_str)
    return matches[0] if matches else ""


def _query_teamviewer_version() -> str:
    """Safely get TeamViewer version."""
    with contextlib.suppress(subprocess.CalledProcessError):
        cmd = 'sudo teamviewer -info | grep "TeamViewer"'
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=True, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        return _extract_teamviewer_version(result)
    return "--"


def get_teamviewer_path() -> Path:
    # Check if any of the possible paths contain the TeamViewer executable
    possible_paths = [
        Path("/usr/bin/teamviewer"),
        Path("/usr/local/bin/teamviewer"),
        Path("/opt/teamviewer/bin/teamviewer"),
        Path("~/.local/bin/teamviewer").expanduser(),
    ]
    return next((path for path in possible_paths if path.is_file()), False)


@cache
def is_teamviewer_installed() -> bool:
    """Check if TeamViewer is installed on a Linux system."""
    return get_teamviewer_path() is not False


@cache
def get_teamviewer_id() -> str:
    """Convenience method to do 3 method calls in one."""
    result = _extract_teamviewer_id(_query_teamviewer_id())
    return f"{int(result):,}".replace(",", " ") if result != "" else "--"


@cache
def get_teamviewer_version() -> str:
    """Get TeamViewer version."""
    return _query_teamviewer_version()


@cache
def get_teamviewer_info() -> dict:
    """Return a dict of Teamviewer info."""
    return {
        "id": get_teamviewer_id(),
        "version": get_teamviewer_version(),
        "path": str(get_teamviewer_path()),
        "is_installed": is_teamviewer_installed(),
    }
