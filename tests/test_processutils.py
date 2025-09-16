import subprocess
import sys
import time

import psutil
import pytest

from process_inspector.utils import processutils

pytestmark = pytest.mark.skipif(
    sys.platform == "linux", reason="Linux not supported yet"
)


# @pytest.fixture
# def process():
#     if sys.platform == "win32":
#         return "explorer.exe"
#     return "Finder"


@pytest.fixture
def process():
    if sys.platform == "win32":
        return "python.exe"
    return "python"


@pytest.fixture
def invalid_process():
    if sys.platform == "win32":
        return "invalid-process.exe"
    return "InvalidProcess"


@pytest.fixture
def killable_process():
    return [sys.executable, "-c", "import time; time.sleep(30)"]


def test_get_process_by_name_timing(process):
    benchmark_time = 0.5
    start = time.time()
    proc = processutils.get_process_by_name(process)
    elapsed = time.time() - start
    assert elapsed < benchmark_time, (
        f"get_process_by_name took too long: {elapsed:.3f} seconds, "
        f"expected less than {benchmark_time} seconds"
    )
    assert proc is not None


def test_get_process_by_name(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    assert isinstance(proc, psutil.Process)


def test_get_process_by_name_invalid(invalid_process):
    proc = processutils.get_process_by_name(invalid_process)
    assert proc is None


def test_get_process_by_pid(process):
    proc = processutils.get_process_by_name(process)
    proc = processutils.get_process_by_pid(proc.pid)
    assert isinstance(proc, psutil.Process)


def test_get_process_by_pid_invalid():
    proc = processutils.get_process_by_pid(999999)
    assert proc is None


def test_is_process_running_by_name(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    is_running = processutils.is_process_running_by_pid(proc.pid)
    assert is_running is True


def test_is_process_running_by_name_invalid(invalid_process):
    is_running = processutils.is_process_running_by_name(invalid_process)
    assert is_running is False


def test_is_process_running_by_pid(process):
    proc = processutils.get_process_by_name(process)
    is_running = processutils.is_process_running_by_pid(proc.pid)
    assert is_running is True


def test_is_process_running_by_name_timing(process):
    benchmark_time = 0.5
    start = time.time()
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    is_running = processutils.is_process_running_by_pid(proc.pid)
    assert is_running is True
    elapsed = time.time() - start
    assert elapsed < benchmark_time, (
        f"get_process_by_name took too long: {elapsed:.3f} seconds, "
        f"expected less than {benchmark_time} seconds"
    )
    assert proc is not None


def test_is_process_running_by_pid_invalid():
    is_running = processutils.is_process_running_by_pid(999999)
    assert is_running is False


def test_kill_process(killable_process):
    proc = subprocess.Popen(killable_process)  # noqa: S603
    time.sleep(1)

    ps_proc = processutils.get_process_by_pid(proc.pid)
    assert ps_proc is not None
    killed = processutils.kill_process(ps_proc)
    assert killed is True
    assert not ps_proc.is_running()


def test_get_mem_usage(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    mem_usage = processutils.get_mem_usage(proc)
    assert isinstance(mem_usage, str)
    assert mem_usage != ""


def test_get_vmem_usage(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    vmem_usage = processutils.get_vmem_usage(proc)
    assert isinstance(vmem_usage, str)
    assert vmem_usage != ""


def test_get_mem_usage_perc(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    mem_perc = processutils.get_mem_usage_perc(proc)
    assert isinstance(mem_perc, str)
    assert mem_perc.endswith("%")


def test_get_proc_usage(process):
    proc = processutils.get_process_by_name(process)
    assert proc is not None
    cpu_usage = processutils.get_proc_usage(proc)
    assert isinstance(cpu_usage, str)
    assert cpu_usage.endswith("%")


def test_get_uptime(process):
    proc = processutils.get_process_by_name(process)
    uptime = processutils.get_uptime(proc)
    assert isinstance(uptime, int)
    assert uptime > 0


def test_get_uptime_as_string(process):
    proc = processutils.get_process_by_name(process)
    uptime_str = processutils.get_uptime_as_string(proc)
    assert isinstance(uptime_str, str)
    assert len(uptime_str) > 0


def test_get_process_info(process):
    proc = processutils.get_process_by_name(process)
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
