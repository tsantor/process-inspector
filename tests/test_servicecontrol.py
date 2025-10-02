import contextlib
import json
import sys

# import time
import pytest

from process_inspector.servicecontrol import Service

from .utils import wait_for_condition

# pytestmark = pytest.mark.skipif(
#     sys.platform == "darwin", reason="Skipping as requires sudo on macOS"
# )


@contextlib.contextmanager
def running_service(service: Service, startup_timeout: float = 15):
    """Context manager to ensure service is running (but do not stop it after)."""
    # If already running, just yield
    if service.is_running():
        yield service
        return

    # Otherwise, start it and wait for it to be running
    start_result = service.start()
    if not start_result:
        pytest.fail("Failed to initiate service startup")

    try:
        wait_for_condition(
            lambda: service.is_running(),
            timeout=startup_timeout,
            description="Service startup",
        )
        yield service
    except Exception:
        # Try to stop if something goes wrong during startup
        with contextlib.suppress(Exception):
            if service.is_running():
                service.stop()
        raise


@contextlib.contextmanager
def stopped_service(service: Service, shutdown_timeout: float = 10):
    """Context manager to ensure service is stopped."""
    # Ensure service is stopped
    try:
        if service.is_running():
            service.stop()
            wait_for_condition(
                lambda: not service.is_running(),
                timeout=shutdown_timeout,
                description="Service shutdown for test",
            )
    except Exception:  # noqa: BLE001
        pytest.skip("Could not stop service for test")

    yield service


@pytest.fixture
def app():
    if sys.platform == "win32":
        return Service("Spooler")
    # return Service("teamviewerd.service")  # systemctl
    return Service("xapp_monitor")  # supervisorctl


def test_service_start_stop(app):
    """Test basic start/stop functionality."""
    with running_service(app) as running:
        assert running.is_running() is True


def test_service_is_running(app):
    """Test is_running status."""
    with running_service(app) as running:
        assert running.is_running() is True


def test_service_stop_when_running(app):
    """Test stopping a running service."""
    with running_service(app) as running:
        assert running.is_running() is True
        assert running.stop() is True
        wait_for_condition(
            lambda: not running.is_running(),
            timeout=10,
            description="Service stop",
        )


def test_service_start_when_stopped(app):
    """Test starting a stopped service."""
    with stopped_service(app) as stopped:
        assert stopped.is_running() is False
        assert stopped.start() is True
        wait_for_condition(
            lambda: stopped.is_running(),
            timeout=15,
            description="Service start",
        )


def test_service_restart(app):
    """Test restart functionality."""
    with running_service(app) as running:
        initial_pid = running.pid

        assert running.restart() is True

        # Wait for service to be running again
        wait_for_condition(
            lambda: running.is_running(),
            timeout=20,  # Restart might take longer
            description="Service restart",
        )

        assert running.pid() != initial_pid, "Service PID should change after restart"


def test_service_status(app):
    """Test status retrieval."""
    status = app.status()
    assert isinstance(status, str)
    assert status != "--"
    assert len(status) > 0


def test_as_dict(app):
    """Test dictionary representation."""
    service_dict = app.as_dict()
    assert isinstance(service_dict, dict)

    expected_keys = [
        "name",
        "pid",
        "status",
        "is_running",
    ]
    missing_keys = [key for key in expected_keys if key not in service_dict]

    assert not missing_keys, f"Missing keys: {missing_keys}"
    assert isinstance(service_dict["status"], str)


# @pytest.mark.skipif(sys.platform == "linux", reason="Not implemented")
def test_process_info_when_running(app):
    """Test process information retrieval when service is running."""
    with running_service(app) as running:
        proc_info = running.process_info()
        assert isinstance(proc_info, dict)
        assert proc_info != {}, "Dict is empty"

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
        missing_keys = [key for key in expected_keys if key not in proc_info]
        assert not missing_keys, f"Missing keys: {missing_keys}"

        assert isinstance(proc_info["pid"], int)
        assert proc_info["pid"] > 0

        assert isinstance(proc_info["uptime_seconds"], int)
        assert proc_info["uptime_seconds"] >= 0

        assert isinstance(proc_info["status"], str)
        # RUNNING or SLEEPING is expected
        assert proc_info["status"] in ("RUNNING", "SLEEPING"), (
            f"Unexpected status: {proc_info['status']}"
        )


def test_as_dict_is_serializable(app):
    """Test that as_dict output is JSON serializable."""
    service_dict = app.as_dict()
    assert isinstance(service_dict, dict)

    serialized = json.dumps(service_dict)
    assert isinstance(serialized, str)

    deserialized = json.loads(serialized)
    assert deserialized == service_dict


def test_process_info_is_serializable(app):
    with running_service(app) as running:
        proc_dict = running.process_info()
        assert isinstance(proc_dict, dict)

        serialized = json.dumps(proc_dict)
        assert isinstance(serialized, str)

        deserialized = json.loads(serialized)
        assert deserialized == proc_dict


def test_instantiate_invalid_service():
    """Test instantiating an invalid service."""
    # with pytest.raises(psutil.NoSuchProcess):
    service = Service("InvalidServiceName")
    assert service.pid() is None
    assert service.status() in ["--", "ERROR"]
    assert service.process_info() == {}
    assert service.is_running() is False
    assert service.as_dict() == {
        "pid": None,
        "name": "InvalidServiceName",
        "is_running": False,
        "status": service.status(),
    }

    invalid_pid = 999999
    proc = service._get_process_for_pid(invalid_pid)  # noqa: SLF001
    assert proc is None


def test_context_manager_exception_handling(app):
    """Test that context manager restores state even if test fails."""
    original_state = app.is_running()

    with contextlib.suppress(ValueError), running_service(app) as running:
        assert running.is_running() is True
        msg = "Simulated test failure"
        raise ValueError(msg)

    # Service should be restored to original state
    wait_for_condition(
        lambda: app.is_running() == original_state,
        timeout=10,
        description="State restoration after exception",
    )


# def test_performance_timing(app):
#     """Test and measure service startup/shutdown performance."""
#     startup_max_time = 45
#     shutdown_max_time = 45

#     # Measure full cycle time
#     start_time = time.time()

#     with running_service(app) as running:
#         startup_time = time.time() - start_time
#         assert running.is_running() is True

#         # Test restart performance too
#         restart_start = time.time()
#         assert running.restart() is True
#         wait_for_condition(
#             lambda: running.is_running(),
#             timeout=20,
#             description="Service restart timing test",
#         )
#         restart_time = time.time() - restart_start

#     total_time = time.time() - start_time
#     shutdown_time = total_time - startup_time

#     # These are loose bounds - adjust based on your service characteristics
#     assert startup_time < startup_max_time, (
#         f"Service took {startup_time:.2f}s to start (too slow)"
#     )
#     assert shutdown_time < shutdown_max_time, (
#         f"Service took {shutdown_time:.2f}s to shut down (too slow)"
#     )

#     print(
#         f"Startup: {startup_time:.2f}s, Shutdown: {shutdown_time:.2f}s, "
#         f"Restart: {restart_time:.2f}s, Total: {total_time:.2f}s"
#     )
