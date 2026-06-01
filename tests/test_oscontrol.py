from __future__ import annotations

import subprocess
from unittest.mock import Mock
from unittest.mock import patch

from process_inspector.oscontrol.runtime.reboot_service import RebootService


def test_reboot_service_success():
    service = RebootService()
    proc = Mock(returncode=0)

    with patch("subprocess.run", return_value=proc) as run_mock:
        assert service.reboot(["sudo", "reboot"]) is True
        run_mock.assert_called_once_with(
            ["sudo", "reboot"],
            check=True,
            capture_output=True,
        )


def test_reboot_service_failure():
    service = RebootService()

    with patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, ["sudo", "reboot"]),
    ):
        assert service.reboot(["sudo", "reboot"]) is False
