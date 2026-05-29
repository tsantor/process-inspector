import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import psutil
import pytest

from process_inspector.utils import processutils

pytestmark = pytest.mark.skipif(
    sys.platform == "linux", reason="Linux not supported yet"
)


@pytest.fixture
def process_name():
    if sys.platform == "win32":
        return "python.exe"
    return "python"


@pytest.fixture
def invalid_process_name():
    if sys.platform == "win32":
        return "invalid-process.exe"
    return "InvalidProcess"


@pytest.fixture
def proc():
    """Fixture to return the current Python process."""
    return psutil.Process()


@pytest.fixture
def killable_process():
    return [sys.executable, "-c", "import time; time.sleep(30)"]


def test_get_process_by_name_timing(proc):
    benchmark_time = 0.5
    start = time.perf_counter()
    elapsed = time.perf_counter() - start
    assert elapsed < benchmark_time, (
        f"get_process_by_name took too long: {elapsed:.3f} seconds, "
        f"expected less than {benchmark_time} seconds"
    )


def test_get_process_by_name(process_name):
    proc = processutils.get_process_by_name(process_name)
    assert isinstance(proc, psutil.Process)


def test_get_process_by_name_invalid(invalid_process_name):
    proc = processutils.get_process_by_name(invalid_process_name)
    assert proc is None


def test_get_process_by_pid(proc):
    proc = processutils.get_process_by_pid(proc.pid)
    assert isinstance(proc, psutil.Process)


def test_get_process_by_pid_invalid():
    proc = processutils.get_process_by_pid(999999)
    assert proc is None


def test_is_process_running_by_name(process_name):
    is_running = processutils.is_process_running_by_name(process_name)
    assert is_running is True


def test_is_process_running_by_name_path(process_name):
    is_running = processutils.is_process_running_by_name(Path(process_name))
    assert is_running is True


def test_is_process_running_by_name_invalid(invalid_process_name):
    is_running = processutils.is_process_running_by_name(invalid_process_name)
    assert is_running is False


def test_is_process_running_by_pid(proc):
    is_running = processutils.is_process_running_by_pid(proc.pid)
    assert is_running is True


def test_is_process_running_by_name_timing(proc):
    benchmark_time = 0.5
    start = time.perf_counter()
    is_running = processutils.is_process_running_by_pid(proc.pid)
    assert is_running is True
    elapsed = time.perf_counter() - start
    assert elapsed < benchmark_time, (
        f"get_process_by_name took too long: {elapsed:.3f} seconds, "
        f"expected less than {benchmark_time} seconds"
    )


def test_is_process_running_by_pid_invalid():
    is_running = processutils.is_process_running_by_pid(999999)
    assert is_running is False


def test_get_mem_usage(proc):
    mem_usage = processutils.get_mem_usage(proc)
    assert isinstance(mem_usage, str)
    assert mem_usage != ""


def test_get_vmem_usage(proc):
    vmem_usage = processutils.get_vmem_usage(proc)
    assert isinstance(vmem_usage, str)
    assert vmem_usage != ""


def test_get_mem_usage_perc(proc):
    mem_perc = processutils.get_mem_usage_perc(proc)
    assert isinstance(mem_perc, str)
    assert mem_perc.endswith("%")


def test_get_proc_usage(proc):
    cpu_usage = processutils.get_proc_usage(proc)
    assert isinstance(cpu_usage, str)
    assert cpu_usage.endswith("%")


def test_get_uptime(proc):
    uptime = processutils.get_uptime(proc)
    assert isinstance(uptime, int)
    assert uptime >= 0


def test_get_uptime_as_string(proc):
    uptime_str = processutils.get_uptime_as_string(proc)
    assert isinstance(uptime_str, str)
    assert len(uptime_str) > 0


def test_get_process_info(proc):
    proc_info = processutils.get_process_info(proc)
    assert isinstance(proc_info, dict)
    expected_keys = [
        "pid",
        "status",
        "mem_usage_percent",
        "mem_usage",
        "vmem_usage",
        "proc_usage",
        "uptime_seconds",
        "uptime",
    ]
    assert all(key in proc_info for key in expected_keys)
    assert isinstance(proc_info["pid"], int)
    assert isinstance(proc_info["status"], str)
    assert isinstance(proc_info["mem_usage_percent"], str)
    assert isinstance(proc_info["mem_usage"], str)
    assert isinstance(proc_info["vmem_usage"], str)
    assert isinstance(proc_info["proc_usage"], str)
    assert isinstance(proc_info["uptime_seconds"], int)
    assert isinstance(proc_info["uptime"], str)


def test_get_process_info_cpu_percent_called_with_interval_none():
    process = MagicMock()
    mem_info = MagicMock(rss=1024, vms=2048)
    oneshot_ctx = MagicMock()
    oneshot_ctx.__enter__.return_value = None
    oneshot_ctx.__exit__.return_value = None

    process.pid = 123
    process.status.return_value = "running"
    process.memory_percent.return_value = 3.14
    process.memory_info.return_value = mem_info
    process.cpu_percent.return_value = 7.5
    process.create_time.return_value = 10.0
    process.oneshot.return_value = oneshot_ctx

    with patch("process_inspector.utils.processutils.time.time", return_value=20.0):
        proc_info = processutils.get_process_info(process)

    process.cpu_percent.assert_called_once_with(interval=None)
    assert proc_info["proc_usage"] == "7.5%"


def test_get_process_info_avoids_duplicate_memory_info_and_create_time_calls():
    process = MagicMock()
    mem_info = MagicMock(rss=1024, vms=2048)
    oneshot_ctx = MagicMock()
    oneshot_ctx.__enter__.return_value = None
    oneshot_ctx.__exit__.return_value = None

    process.pid = 123
    process.status.return_value = "running"
    process.memory_percent.return_value = 3.14
    process.memory_info.return_value = mem_info
    process.cpu_percent.return_value = 7.5
    process.create_time.return_value = 10.0
    process.oneshot.return_value = oneshot_ctx

    with patch("process_inspector.utils.processutils.time.time", return_value=20.0):
        processutils.get_process_info(process)

    process.memory_info.assert_called_once_with()
    process.create_time.assert_called_once_with()


def test_debug_process_info(proc):
    proc_info = processutils.debug_process_info(proc)
    assert isinstance(proc_info, dict)
    expected_keys = ["pid", "name", "exe", "cmdline", "create_time", "status"]
    assert all(key in proc_info for key in expected_keys)


def test_kill_process(killable_process):
    proc = subprocess.Popen(killable_process)  # noqa: S603
    time.sleep(1)

    ps_proc = processutils.get_process_by_pid(proc.pid)
    assert ps_proc is not None
    killed = processutils.kill_process(ps_proc)
    assert killed is True
    assert not ps_proc.is_running()


def test_kill_process_no_such_process():
    """Test kill_process when psutil.NoSuchProcess is raised."""
    mock_process = MagicMock()
    mock_process.kill.side_effect = psutil.NoSuchProcess(pid=1234)

    result = processutils.kill_process(mock_process)
    assert result is False


def test_kill_process_access_denied():
    """Test kill_process when psutil.AccessDenied is raised."""
    mock_process = MagicMock()
    mock_process.kill.side_effect = psutil.AccessDenied(pid=1234)

    result = processutils.kill_process(mock_process)
    assert result is False


def test_kill_process_zombie_process():
    """Test kill_process when psutil.ZombieProcess is raised."""
    mock_process = MagicMock()
    mock_process.kill.side_effect = psutil.ZombieProcess(pid=1234)

    result = processutils.kill_process(mock_process)
    assert result is False


def test_kill_process_timeout_expired():
    """Test kill_process when psutil.TimeoutExpired is raised."""
    mock_process = MagicMock()
    mock_process.kill.return_value = None  # Simulate successful kill
    mock_process.wait.side_effect = psutil.TimeoutExpired(pid=1234, seconds=3)

    result = processutils.kill_process(mock_process)
    assert result is False
