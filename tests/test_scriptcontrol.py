import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import process_inspector.scriptcontrol.mac as scriptcontrol
from process_inspector.scriptcontrol import Script


def test_run_script_success():
    """Test run_script when the script executes successfully."""
    mock_result = MagicMock()
    mock_result.stdout = "Script output"
    mock_result.returncode = 0

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        result = scriptcontrol.run_script(Path("/path/to/script.sh"))
        assert result is True
        mock_run.assert_called_once_with(
            ["/opt/homebrew/bin/bash", Path("/path/to/script.sh")],
            check=True,
            capture_output=True,
            text=True,
        )


def test_run_script_failure():
    """Test run_script when the script execution fails."""
    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "cmd", stderr="Error"),
    ) as mock_run:
        result = scriptcontrol.run_script(Path("/path/to/script.sh"))
        assert result is False
        mock_run.assert_called_once_with(
            ["/opt/homebrew/bin/bash", Path("/path/to/script.sh")],
            check=True,
            capture_output=True,
            text=True,
        )


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
