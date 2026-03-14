from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from process_inspector.servicecontrol.implementations.supervisorctl import SupervisorCtl


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_stop_updates_running_state_to_false_from_status():
    callback = MagicMock()
    ctl = SupervisorCtl("example", state_change_callback=callback)
    ctl.status = MagicMock(return_value="STOPPED")

    with patch("subprocess.run") as run:
        run.return_value = MagicMock(stdout="example: stopped\n", returncode=0)
        assert ctl.stop() is True

    callback.assert_called_with(service=ctl, is_running=False)


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_restart_updates_running_state_from_status():
    callback = MagicMock()
    ctl = SupervisorCtl("example", state_change_callback=callback)
    ctl.status = MagicMock(return_value="RUNNING")

    with patch("subprocess.run") as run:
        run.return_value = MagicMock(stdout="example: started\n", returncode=0)
        assert ctl.restart() is True

    callback.assert_called_with(service=ctl, is_running=True)
