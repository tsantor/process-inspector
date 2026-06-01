from __future__ import annotations

import re
import shlex
import subprocess
from typing import TYPE_CHECKING

from process_inspector.utils.stringutils import extract_version

if TYPE_CHECKING:
    from pathlib import Path


def launch_mac_app(path: Path) -> bool:
    proc = subprocess.Popen(  # noqa: S603
        ["open", str(path)],  # noqa: S607
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    _, stderr = proc.communicate(timeout=5)
    return not bool(stderr)


def quit_mac_app(app_name: str) -> None:
    cmd = f'tell application "{app_name}" to quit'
    subprocess.run(["osascript", "-e", cmd], check=True)  # noqa: S603, S607


def read_mac_app_version(path: Path) -> str:
    cmd = ["mdls", "-name", "kMDItemVersion", str(path)]
    proc = subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    matches = re.search(r"(\d{1,}\.?)+", proc.stdout.strip())
    return matches[0] if matches else "--"


def launch_windows_app(path: Path) -> None:
    subprocess.Popen([str(path)])  # noqa: S603


def read_windows_app_version(path: Path) -> str:
    escaped_path = str(path).replace("\\", "\\\\")
    cmd = [
        "powershell",
        "-command",
        f"""(Get-Item -Path \"{escaped_path}\").VersionInfo.ProductVersion""",
    ]
    proc = subprocess.run(  # noqa: S603
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    matches = re.search(r"(\d{1,}\.?)+", proc.stdout.strip())
    return matches[0] if matches else "--"


def read_linux_app_version(path: Path) -> str:
    cmd = f"{path} --version"
    proc = subprocess.run(  # noqa: S603
        shlex.split(cmd),
        check=True,
        text=True,
        capture_output=True,
    )
    return extract_version(proc.stdout.strip())
