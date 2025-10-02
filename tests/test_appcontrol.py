import contextlib
import json
import sys
from pathlib import Path

import pytest

from process_inspector.appcontrol import NativeApp

from .utils import wait_for_condition

pytestmark = pytest.mark.skipif(
    sys.platform == "linux", reason="Linux not supported yet"
)


@contextlib.contextmanager
def running_app(
    app: NativeApp, startup_timeout: float = 15, shutdown_timeout: float = 10
):
    """Context manager to ensure app is running and properly cleaned up."""
    # Ensure clean state before starting
    try:
        if app.is_running():
            app.close()
            wait_for_condition(
                lambda: not app.is_running(),
                timeout=shutdown_timeout,
                description="Pre-test app cleanup",
            )
    except Exception:  # noqa: BLE001
        # If we can't clean up, skip this iteration
        pytest.skip("Could not clean up app before test")

    # Start the app
    start_result = app.open()
    if not start_result:
        pytest.fail("Failed to initiate app startup")

    try:
        # Wait for app to be fully running
        wait_for_condition(
            lambda: app.is_running(),
            timeout=startup_timeout,
            description="App startup",
        )

        # Yield the running app
        yield app

    except Exception:
        # If something goes wrong, still try to clean up
        with contextlib.suppress(Exception):
            if app.is_running():
                app.close()
        # Raise the original exception
        raise

    finally:
        # Always attempt cleanup
        try:
            if app.is_running():
                app.close()
                # if close_result:
                wait_for_condition(
                    lambda: not app.is_running(),
                    timeout=shutdown_timeout,
                    description="App shutdown",
                )
        except Exception as cleanup_error:  # noqa: BLE001
            # Log cleanup failure but don't fail the test
            print(f"Warning: App cleanup failed: {cleanup_error}")  # noqa: T201


@contextlib.contextmanager
def app_if_needed(
    app: NativeApp,
    need_running: bool = True,
    startup_timeout: float = 15,
    shutdown_timeout: float = 10,
):
    """Context manager that only starts app if needed."""
    if need_running:
        with running_app(app, startup_timeout, shutdown_timeout) as running:
            yield running
    else:
        # Ensure app is NOT running
        if app.is_running():
            app.close()
            wait_for_condition(
                lambda: not app.is_running(),
                timeout=shutdown_timeout,
                description="App shutdown for non-running test",
            )
        yield app


@pytest.fixture
def app():
    if sys.platform == "win32":
        return NativeApp(Path("C:/Program Files/Sublime Text/sublime_text.exe"))
    return NativeApp(Path("/Applications/Safari.app"))


def test_app_open_close(app):
    """Test basic open/close functionality."""
    with running_app(app) as running:
        assert running.is_running() is True

    # App should be closed after context exit
    assert app.is_running() is False


def test_app_is_running(app):
    """Test is_running status."""
    with running_app(app) as running:
        assert running.is_running() is True


def test_close_when_app_not_running(app):
    """Test closing an app that's not running."""
    with app_if_needed(app, need_running=False) as stopped:
        assert stopped.is_running() is False
        assert stopped.close() is True


def test_app_version(app):
    """Test version retrieval - doesn't need app running."""
    assert isinstance(app.get_version(), str)
    assert app.get_version() != "--"


def test_as_dict(app):
    """Test dictionary representation."""
    app_dict = app.as_dict()
    assert isinstance(app_dict, dict)
    expected_keys = [
        "exe",
        "name",
        "path",
        "is_installed",
        "version",
        "install_date",
        "install_date_short",
    ]
    assert all(key in app_dict for key in expected_keys)

    # Type checks
    assert isinstance(app_dict["install_date"], str)
    assert isinstance(app_dict["install_date_short"], str)
    assert isinstance(app_dict["version"], str)
    assert isinstance(app_dict["is_installed"], bool)
    assert app_dict["is_installed"] is True

    # Value checks
    assert app_dict["exe"] == app.app_exe
    assert app_dict["name"] == app.app_name
    assert app_dict["path"] == str(app.app_path)


def test_process_info(app):
    """Test process information retrieval."""
    with running_app(app) as running:
        proc_info = running.process_info()
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

        # Type validation
        assert isinstance(proc_info["pid"], int)
        assert isinstance(proc_info["status"], str)
        assert isinstance(proc_info["mem_usage_percent"], str)
        assert isinstance(proc_info["mem_usage"], str)
        assert isinstance(proc_info["vmem_usage"], str)
        assert isinstance(proc_info["proc_usage"], str)
        assert isinstance(proc_info["uptime_seconds"], int)
        assert isinstance(proc_info["uptime"], str)

        # Sanity checks
        assert proc_info["pid"] > 0
        assert proc_info["uptime_seconds"] >= 0


def test_as_dict_is_serializable(app):
    """Test that as_dict output is JSON serializable."""
    app_dict = app.as_dict()
    serialized = json.dumps(app_dict)
    assert isinstance(serialized, str)

    deserialized = json.loads(serialized)
    assert deserialized == app_dict


def test_process_info_is_serializable(app):
    """Test that process_info output is JSON serializable."""
    with running_app(app) as running:
        proc_info = running.process_info()
        serialized = json.dumps(proc_info)
        assert isinstance(serialized, str)

        deserialized = json.loads(serialized)
        assert deserialized == proc_info


# def test_multiple_operations_same_session(app):
#     """Test multiple operations within the same app session."""
#     with running_app(app) as running:
#         # Multiple is_running checks
#         assert running.is_running() is True
#         assert running.is_running() is True

#         # Get process info multiple times
#         proc_info1 = running.process_info()
#         time.sleep(0.1)
#         proc_info2 = running.process_info()

#         # PID should remain consistent
#         assert proc_info1["pid"] == proc_info2["pid"]
#         assert proc_info1["status"] == proc_info2["status"]


def test_context_manager_exception_handling(app):
    """Test that context manager cleans up even if test fails."""
    with contextlib.suppress(ValueError), running_app(app) as running:
        assert running.is_running() is True
        msg = "Simulated test failure"
        raise ValueError(msg)

    # App should still be cleaned up
    wait_for_condition(
        lambda: not app.is_running(),
        timeout=5,
        description="Cleanup after exception",
    )


def test_app_not_running_between_tests(app):
    """Verify app is not running at start of test."""
    assert app.is_running() is False


# def test_performance_timing(app):
#     """Test and measure app startup/shutdown performance."""
#     startup_max_time = 10
#     shutdown_max_time = 5
#     start_time = time.time()

#     with running_app(app) as running:
#         startup_time = time.time() - start_time
#         assert running.is_running() is True

#     total_time = time.time() - start_time
#     shutdown_time = total_time - startup_time

#     # These are loose bounds - adjust based on your app's characteristics
#     assert startup_time < startup_max_time, (
#         f"App took {startup_time:.2f}s to start (too slow)"
#     )
#     assert shutdown_time < shutdown_max_time, (
#         f"App took {shutdown_time:.2f}s to shut down (too slow)"
#     )

#     print(
#         f"Startup: {startup_time:.2f}s, Shutdown: {shutdown_time:.2f}s, Total: {total_time:.2f}s"
#     )
