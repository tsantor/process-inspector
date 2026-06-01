from __future__ import annotations

import subprocess


class RebootService:
    def reboot(self, command: list[str]) -> bool:
        try:
            proc = subprocess.run(  # noqa: S603
                list(command), check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            return False
        return proc.returncode == 0
