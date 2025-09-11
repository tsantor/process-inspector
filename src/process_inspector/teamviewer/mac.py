import contextlib
import shlex
import subprocess
from functools import cache
from pathlib import Path


@cache
def is_teamviewer_installed() -> bool:
    """
    Check if TeamViewer is installed on a Mac by verifying the existence of
    the application bundle.

    :return: True if TeamViewer is installed, False otherwise
    """
    # Path where TeamViewer is typically installed on macOS
    teamviewer_path = Path("/Applications/TeamViewer.app")

    # Check if the TeamViewer application bundle exists
    return teamviewer_path.exists()


def _query_teamviewer_id() -> str:
    """Safely get TeamViewer ID from command line."""
    paths = [
        Path("/Library/Preferences/com.teamviewer.teamviewer.preferences.plist"),
        Path(
            "~/Library/Preferences/com.teamviewer.teamviewer.preferences.Machine.plist"
        ).expanduser(),
    ]

    file = next((path for path in paths if path.is_file()), None)

    if file:
        with contextlib.suppress(subprocess.CalledProcessError):
            key = "ClientID"
            cmd = f"defaults read {file} {key}"
            proc = subprocess.run(  # noqa: S603
                shlex.split(cmd), check=True, capture_output=True, text=True
            )
            return proc.stdout.strip()
    return "--"  # pragma: no cover


def _query_teamviewer_version() -> str:
    """Safely get TeamViewer version from command line."""
    paths = [
        Path("/Library/Preferences/com.teamviewer.teamviewer.preferences.plist"),
        Path(
            "~/Library/Preferences/com.teamviewer.teamviewer.preferences.Machine.plist"
        ).expanduser(),
    ]

    file = next((path for path in paths if path.is_file()), None)

    if file:
        with contextlib.suppress(subprocess.CalledProcessError):
            key = "Version"
            cmd = f"defaults read {file} {key}"
            proc = subprocess.run(  # noqa: S603
                shlex.split(cmd), check=True, capture_output=True, text=True
            )
            return proc.stdout.strip()
    return "--"  # pragma: no cover


@cache
def get_teamviewer_id() -> str:
    """Get TeamViewer ID."""
    if result := _query_teamviewer_id():
        return f"{int(result):,}".replace(",", " ")
    return "--"  # pragma: no cover


@cache
def get_teamviewer_version() -> str:
    """Get TeamViewer version."""
    return _query_teamviewer_version()


def get_teamviewer_path() -> Path:
    return Path("/Applications/TeamViewer.app")


def get_teamviewer_info() -> dict:
    """Return a dict of Teamviewer info."""
    return {
        "id": get_teamviewer_id(),
        "version": get_teamviewer_version(),
        "path": str(get_teamviewer_path()),
        "is_installed": is_teamviewer_installed(),
    }
