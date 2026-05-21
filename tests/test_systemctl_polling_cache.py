# ruff: noqa: SLF001 PLR2004

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from process_inspector.servicecontrol.implementations.systemctl import SystemCtl


def _mock_proc(stdout: str, returncode: int = 0):
    proc = MagicMock()
    proc.stdout = stdout
    proc.returncode = returncode
    return proc


@patch.object(SystemCtl, "service_control_path", Path("/usr/bin/systemctl"))
def test_is_running_then_process_info_uses_single_show_command():
    ctl = SystemCtl("teamviewerd.service")
    ctl._runtime._runtime_port.load_process = lambda _pid: object()
    ctl._runtime._runtime_port.get_process_info = lambda _process: {"pid": 123}
    with patch("subprocess.run") as run:
        run.return_value = _mock_proc(
            "LoadState=loaded\nActiveState=active\nSubState=running\nMainPID=123\n"
        )
        assert ctl.is_running() is True
        info = ctl.process_info()

    assert isinstance(info, dict)
    assert run.call_count == 1
    assert run.call_args_list[0].args[0][-2:] == ["show", "teamviewerd.service"]


@patch.object(SystemCtl, "service_control_path", Path("/usr/bin/systemctl"))
def test_status_mapping_from_show_output():
    ctl = SystemCtl("teamviewerd.service")
    with patch("subprocess.run") as run:
        run.side_effect = [
            _mock_proc("LoadState=loaded\nActiveState=active\nSubState=running\n"),
            _mock_proc("LoadState=loaded\nActiveState=inactive\nSubState=dead\n"),
            _mock_proc("LoadState=loaded\nActiveState=failed\nSubState=failed\n"),
            _mock_proc("LoadState=loaded\nActiveState=activating\nSubState=start\n"),
            _mock_proc("LoadState=loaded\nActiveState=deactivating\nSubState=stop\n"),
            _mock_proc("LoadState=not-found\n"),
        ]
        ctl.reset_cache()
        assert ctl.status() == "RUNNING"
        ctl.reset_cache()
        assert ctl.status() == "STOPPED"
        ctl.reset_cache()
        assert ctl.status() == "FAILED"
        ctl.reset_cache()
        assert ctl.status() == "STARTING"
        ctl.reset_cache()
        assert ctl.status() == "STOPPING"
        ctl.reset_cache()
        assert ctl.status() == "--"

    assert run.call_count == 6


@patch.object(SystemCtl, "service_control_path", Path("/usr/bin/systemctl"))
def test_cache_invalidates_on_lifecycle_and_reset_cache():
    ctl = SystemCtl("teamviewerd.service")
    with patch("subprocess.run") as run:
        run.side_effect = [
            _mock_proc(
                "LoadState=loaded\nActiveState=active\nSubState=running\nMainPID=1\n"
            ),
            _mock_proc("", returncode=0),  # start
            _mock_proc("", returncode=0),  # stop
            _mock_proc("", returncode=0),  # restart
            _mock_proc(
                "LoadState=loaded\nActiveState=active\nSubState=running\nMainPID=1\n"
            ),
        ]
        assert ctl.status() == "RUNNING"
        assert ctl.start() is True
        assert ctl.stop() is True
        assert ctl.restart() is True
        ctl.reset_cache()
        assert ctl.status() == "RUNNING"

    assert run.call_count == 5


def test_systemctl_ttl_updated():
    assert SystemCtl._command_cache_ttl_seconds == 3.0
