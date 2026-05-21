# ruff: noqa: SLF001 PLR2004

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

from process_inspector.servicecontrol.implementations.supervisorctl import SupervisorCtl


def _mock_proc(stdout: str, returncode: int = 0):
    proc = MagicMock()
    proc.stdout = stdout
    proc.returncode = returncode
    return proc


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_is_running_then_process_info_reduces_subprocess_calls():
    ctl = SupervisorCtl("example")
    ctl._runtime._runtime_port.load_process = lambda _pid: object()
    ctl._runtime._runtime_port.get_process_info = lambda _process: {"pid": 123}
    with patch("subprocess.run") as run:
        run.side_effect = [
            _mock_proc("example RUNNING pid 123\n"),  # status
        ]
        assert ctl.is_running() is True
        info = ctl.process_info()

    assert isinstance(info, dict)
    assert run.call_count == 1
    assert run.call_args_list[0].args[0][-2:] == ["status", "example"]


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_status_ttl_cache_hit_reduces_invocations():
    ctl = SupervisorCtl("example")
    with patch("subprocess.run") as run:
        run.return_value = _mock_proc("example RUNNING pid 123\n")
        assert ctl.status() == "RUNNING"
        assert ctl.status() == "RUNNING"

    assert run.call_count == 1


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_get_pid_uses_cached_status_output():
    ctl = SupervisorCtl("example")
    with patch("subprocess.run") as run:
        run.return_value = _mock_proc("example RUNNING pid 123, uptime 0:01:00\n")
        assert ctl.status() == "RUNNING"
        assert ctl.get_pid() == 123

    assert run.call_count == 1
    assert run.call_args_list[0].args[0][-2:] == ["status", "example"]


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_is_running_stopped_skips_pid_call_and_preserves_boolean():
    ctl = SupervisorCtl("example")
    with patch("subprocess.run") as run:
        run.return_value = _mock_proc("example STOPPED not running\n")
        assert ctl.is_running() is False

    assert run.call_count == 1
    assert run.call_args_list[0].args[0][-2:] == ["status", "example"]


@patch.object(SupervisorCtl, "service_control_path", Path("/usr/bin/supervisorctl"))
def test_cache_invalidates_on_lifecycle_and_reset_cache():
    ctl = SupervisorCtl("example")

    with patch("subprocess.run") as run:
        run.side_effect = [
            _mock_proc("example RUNNING pid 123\n"),  # status miss
            _mock_proc("example: started\n"),  # start
            _mock_proc("example RUNNING pid 123\n"),  # start -> refresh status
            _mock_proc("example: stopped\n"),  # stop
            _mock_proc("example STOPPED not running\n"),  # stop -> refresh status
            _mock_proc("example: started\n"),  # restart
            _mock_proc("example RUNNING pid 123\n"),  # restart -> refresh status
            _mock_proc("example RUNNING pid 123\n"),  # status miss after reset_cache
        ]

        assert ctl.status() == "RUNNING"
        assert ctl.start() is True
        assert ctl.stop() is True
        assert ctl.restart() is True
        ctl.reset_cache()
        assert ctl.status() == "RUNNING"

    assert run.call_count == 8


def test_supervisor_ttl_updated():
    assert SupervisorCtl._command_cache_ttl_seconds == 5.0
