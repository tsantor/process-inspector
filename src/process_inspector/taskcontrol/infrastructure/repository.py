from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)


class PowerShellRunner:
    def run_powershell_command(
        self, command: list[str], check: bool = True
    ) -> subprocess.CompletedProcess | None:
        command_str = " ".join(command)
        full_command = [
            "powershell",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            command_str,
        ]
        try:
            result = subprocess.run(  # noqa: S603
                full_command,
                capture_output=True,
                text=True,
                check=check,
                encoding="utf-8",
                timeout=20,
            )
            if result.returncode != 0:
                logger.error(
                    "PowerShell command failed with return code %d. Raw STDOUT: %s",
                    result.returncode,
                    result.stdout.strip(),
                )
            return result
        except subprocess.CalledProcessError as exc:
            logger.error(  # noqa: TRY400
                "PowerShell command failed with exit code %d: %s\nStderr: %s",
                exc.returncode,
                exc.cmd,
                exc.stderr.strip(),
            )
            return None
        except FileNotFoundError:
            logger.error("PowerShell executable not found.")  # noqa: TRY400
            return None
        except Exception:
            logger.exception("An unexpected error occurred while running PowerShell")
            return None
