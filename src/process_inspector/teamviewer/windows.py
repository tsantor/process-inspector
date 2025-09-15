import contextlib
import winreg
from functools import cache
from pathlib import Path


def _query_teamviewer_id() -> str:
    """Safely get TeamViewer ID from Windows Registry."""
    with contextlib.suppress(FileNotFoundError):
        key = r"SOFTWARE\Wow6432Node\TeamViewer"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as chnd:
            return winreg.QueryValueEx(chnd, "ClientID")[0]

    with contextlib.suppress(FileNotFoundError):
        key = r"SOFTWARE\TeamViewer"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as chnd:
            return winreg.QueryValueEx(chnd, "ClientID")[0]
    return "--"  # pragma: no cover


def _query_teamviewer_version() -> str:
    """Safely get TeamViewer version from Windows Registry."""
    with contextlib.suppress(FileNotFoundError):
        key = r"SOFTWARE\Wow6432Node\TeamViewer"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as chnd:
            return winreg.QueryValueEx(chnd, "Version")[0]

    with contextlib.suppress(FileNotFoundError):
        key = r"SOFTWARE\TeamViewer"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as chnd:
            return winreg.QueryValueEx(chnd, "Version")[0]
    return "--"  # pragma: no cover


@cache
def get_teamviewer_path() -> Path:
    """Get TeamViewer executable path."""
    possible_paths = [
        Path("C:/Program Files (x86)/TeamViewer/TeamViewer.exe"),
        Path("C:/Program Files/TeamViewer/TeamViewer.exe"),
    ]
    return next((path for path in possible_paths if path.is_file()), "")


@cache
def is_teamviewer_installed() -> bool:
    """
    Check if TeamViewer is installed by verifying the
    existence of common executable paths.

    :return: True if TeamViewer is installed, False otherwise
    """
    # Check if any of the possible paths contain the TeamViewer executable
    possible_paths = [
        Path("C:/Program Files (x86)/TeamViewer/TeamViewer.exe"),
        Path("C:/Program Files/TeamViewer/TeamViewer.exe"),
    ]
    return any(path.is_file() for path in possible_paths)


@cache
def get_teamviewer_id() -> str:
    """Get Teamviewer ID"""
    if result := _query_teamviewer_id():
        return f"{int(result):,}".replace(",", " ")
    return "--"


@cache
def get_teamviewer_version() -> str:
    """Get TeamViewer version."""
    return _query_teamviewer_version().strip()


@cache
def get_teamviewer_info() -> dict:
    """Return a dict of Teamviewer info."""
    return {
        "id": get_teamviewer_id(),
        "version": get_teamviewer_version(),
        "path": str(get_teamviewer_path()),
        "is_installed": is_teamviewer_installed(),
    }
