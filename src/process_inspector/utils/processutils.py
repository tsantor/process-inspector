import contextlib
import logging
import sys
import time
from pathlib import Path

import psutil

from .byteutils import human_readable_bytes
from .datetimeutils import human_delta

logger = logging.getLogger(__name__)


def debug_process_info(proc: psutil.Process) -> dict:
    return proc.as_dict(
        attrs=["pid", "name", "exe", "cmdline", "create_time", "status"]
    )


def get_process_by_name(name, *, newest: bool = True) -> psutil.Process | None:
    """Return a Process by name or None. If newest=True, return the most recently created."""
    # Set name based on platform conventions (stem for macOS, name for others)
    if isinstance(name, Path):
        name = name.stem if sys.platform == "darwin" else name.name

    name = name.lower()
    attrs = (
        ["pid", "name", "create_time"]
        if sys.platform != "linux"
        else ["pid", "name", "cmdline", "create_time"]
    )

    matches = []
    for proc in psutil.process_iter(attrs):
        try:
            proc_name = proc.info["name"].lower()
            if proc_name == name:
                matches.append(proc)
            elif sys.platform == "linux":
                for arg in proc.info.get("cmdline", []):
                    if name in Path(arg).name.lower():
                        matches.append(proc)
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not matches:
        return None

    logger.debug("Found %d processes matching name '%s'", len(matches), name)

    if newest:
        # Return the process with the latest create_time
        return max(matches, key=lambda p: p.info.get("create_time", 0))

    # Return the first match (original behavior)
    return matches[0]


def get_process_by_pid(pid: int) -> psutil.Process | None:
    """Return a Process by PID or None."""
    with contextlib.suppress(psutil.NoSuchProcess):
        return psutil.Process(pid)
    return None


def is_process_running_by_name(name) -> bool:
    """Check if a process is running by name."""
    if isinstance(name, Path):
        # macOS uses the stem, Linux/Windows uses the name
        name = name.stem if sys.platform == "darwin" else name.name
    return proc.is_running() if (proc := get_process_by_name(name)) else False


def is_process_running_by_pid(pid) -> bool:
    """Check if a process is running by PID."""
    return proc.is_running() if (proc := get_process_by_pid(pid)) else False


def kill_process(process: psutil.Process) -> bool:
    """Kill a given process."""
    try:
        process.kill()
        process.wait(timeout=3)
        return True
    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess,
        psutil.TimeoutExpired,
    ):
        logger.error(  # noqa: TRY400
            "Failed to kill process %s with PID %s", process.info["name"], process.pid
        )
        return False


def get_mem_usage(process: psutil.Process) -> str:
    """Return memory usage in human readable units."""
    mem_info = process.memory_info()
    return human_readable_bytes(mem_info.rss, metric=False)


def get_vmem_usage(process: psutil.Process) -> str:
    """Return virtual memory usage in human readable units."""
    mem_info = process.memory_info()
    return human_readable_bytes(mem_info.vms, metric=False)


def get_mem_usage_perc(process: psutil.Process) -> str:
    """Return memory usage as a percent."""
    mem_usage = process.memory_percent()
    return f"{round(mem_usage, 2)}%"


def get_proc_usage(process: psutil.Process) -> str:
    """Return proce usage as a percent."""
    cpu_usage = process.cpu_percent()
    return f"{cpu_usage}%"


def get_uptime(process: psutil.Process) -> int:
    """Return the uptime of a process in seconds."""
    return int(time.time() - process.create_time())


def get_uptime_as_string(process: psutil.Process) -> str:
    """Return uptime as string."""
    return human_delta(get_uptime(process))


def get_process_info(process: psutil.Process) -> dict:
    """Return a dictionary representation of the process."""
    with process.oneshot():
        return {
            "pid": process.pid,
            "status": process.status().upper(),
            "mem_usage_percent": get_mem_usage_perc(process) if process else "--",
            "mem_usage": get_mem_usage(process) if process else "--",
            "vmem_usage": get_vmem_usage(process) if process else "--",
            "proc_usage": get_proc_usage(process) if process else "--",
            "uptime_seconds": get_uptime(process) if process else "--",
            "uptime": get_uptime_as_string(process) if process else "--",
        }
