import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from process_inspector.scriptcontrol import Script
from process_inspector.scriptcontrol.infrastructure.platform_runners import (
    run_windows_script,
)


@pytest.mark.skipif(os.name == "nt", reason="Mac/Linux specific test")
def test_script_execution():
    """Test the Script class with an actual bash script."""
    # Create a temporary bash script
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sh") as temp_script:
        temp_script.write(b"#!/bin/bash\nsleep 1\necho 'Script executed'\n")
        temp_script.flush()
        temp_script_path = Path(temp_script.name)

    # Make the script executable
    temp_script_path.chmod(0o755)

    try:
        script = Script(temp_script_path)
        result = script.run()
        assert result is True
    finally:
        temp_script_path.unlink()


@pytest.mark.skipif(os.name != "nt", reason="Windows-specific test")
def test_script_execution_windows():
    """Test the Script class with an actual PowerShell script."""
    # Create a temporary PowerShell script
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1") as temp_script:
        temp_script.write(b"Start-Sleep -Seconds 1\nWrite-Output 'Script executed'")
        temp_script.flush()
        temp_script_path = Path(temp_script.name)

    try:
        # Run the PowerShell script using the Script class
        script = Script(temp_script_path)
        result = script.run()
        assert result is True
    finally:
        # Clean up the temporary script
        temp_script_path.unlink()


def test_run_script_failure():
    """Test run_script when the script execution fails."""
    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "cmd", stderr="Error"),
    ):
        result = Script(Path("/path/to/script.sh")).run()
        assert result is False


def test_file_not_found_failure():
    """Test run_script when the script execution fails."""
    with patch("subprocess.run", side_effect=FileNotFoundError()):
        result = Script(Path("/path/to/script.sh")).run()
        assert result is False


def test_run_windows_script_uses_powershell_file_mode():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        script_path = Path(r"C:\temp\script.ps1")

        result = run_windows_script(script_path)

        assert result is True
        mock_run.assert_called_once_with(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


def test_run_windows_script_called_process_error_returns_false():
    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "powershell", stderr="Boom"),
    ):
        result = run_windows_script(Path(r"C:\temp\script.ps1"))
        assert result is False
