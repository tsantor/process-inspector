from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _resolve_bash_path(possible_paths: list[str]) -> str | None:
    return next((path for path in possible_paths if Path(path).exists()), None)


def _resolve_powershell_path(possible_paths: list[str]) -> str | None:
    return next(
        (path for path in possible_paths if Path(path).exists()),
        possible_paths[0] if possible_paths else None,
    )


def run_bash_script(path: Path, *, possible_paths: list[str]) -> bool:
    bash_path = _resolve_bash_path(possible_paths)
    if not bash_path:
        logger.warning("Bash executable not found on this system.")
        return False

    try:
        subprocess.run(  # noqa: S603
            [bash_path, path],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Script '%s' executed successfully.", path)
        return True
    except subprocess.CalledProcessError as exc:
        logger.info(
            "Script '%s' execution failed with return code %s. Error: %s",
            path,
            exc.returncode,
            exc.stderr.strip(),
        )
        return False
    except FileNotFoundError:
        logger.warning("Script '%s' not found", path)
        return False


def run_windows_script(path: Path) -> bool:
    powershell_path = _resolve_powershell_path(
        [
            "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
            "C:/Windows/SysWOW64/WindowsPowerShell/v1.0/powershell.exe",
        ]
    )

    try:
        subprocess.run(  # noqa: S603
            [
                powershell_path,
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Script '%s' executed successfully.", path)
        return True
    except subprocess.CalledProcessError as exc:
        logger.info(
            "Script '%s' execution failed with return code %s. Error: %s",
            path,
            exc.returncode,
            exc.stderr.strip(),
        )
        return False
    except FileNotFoundError:
        logger.warning("Script '%s' not found", path)
        return False
