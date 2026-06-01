import contextlib
import json
import sys
from datetime import UTC
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest

from process_inspector.appcontrol import NativeApp
from process_inspector.appcontrol.runtime.app_base import AppControllerBase
from process_inspector.appcontrol.runtime.runtime_service import AppRuntimeService
from process_inspector.appcontrol.runtime.runtime_state import AppRuntimeState

from .utils import wait_for_condition

pytestmark = pytest.mark.skipif(
    sys.platform == "linux", reason="Linux not supported yet"
)


class MockApp(AppControllerBase):
    """Mock implementation of AppControllerBase for testing."""

    def open(self) -> bool:
        return True

    def get_version(self) -> str:
        return "1.0.0"


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
            app.is_running,
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


@pytest.fixture
def mock_app():
    """Fixture to create a mock app instance."""
    return MockApp(Path("/path/to/app"))


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


def test_app_not_running_between_tests(mock_app):
    """Verify app is not running at start of test."""
    assert mock_app.is_running() is False


def test_is_running_no_such_process(mock_app):
    """Test is_running when psutil.NoSuchProcess is raised."""
    with patch("psutil.Process", side_effect=psutil.NoSuchProcess(pid=1234)):
        result = mock_app.is_running()
        assert result is False


def test_is_running_access_denied(mock_app):
    """Test is_running when psutil.AccessDenied is raised."""
    with patch("psutil.Process", side_effect=psutil.AccessDenied(pid=1234)):
        result = mock_app.is_running()
        assert result is False


def test_is_running_os_error(mock_app):
    """Test is_running when OSError is raised."""
    with patch("psutil.Process", side_effect=OSError("Test OSError")):
        result = mock_app.is_running()
        assert result is False


class DummyProcess:
    def __init__(self):
        self.pid = 123
        self._create_time = 1234.0
        self._running = True

    def is_running(self):
        return self._running

    def status(self):
        return "running"

    def create_time(self):
        return self._create_time

    def terminate(self):
        self._running = False

    def kill(self):
        self._running = False

    def wait(self, timeout=0):
        return None


class DummyRuntimePort:
    def __init__(self, process=None):
        self.process = process

    def find_process(self, app_path):
        return self.process

    def load_process(self, pid):
        return self.process

    def is_process_running(self, process):
        return process.is_running()

    def process_status(self, process):
        return process.status()

    def is_process_zombie(self, process):
        return process.status().lower() == "zombie"

    def process_create_time(self, process):
        return process.create_time()

    def terminate_process(self, process):
        process.terminate()

    def kill_process(self, process):
        process.kill()

    def wait_process(self, process, timeout):
        process.wait(timeout)

    def get_process_info(self, process):
        return {"pid": 123, "status": "RUNNING"}

    def human_datetime_short(self, value):
        return value.isoformat()

    def now_utc(self):
        return datetime.now(tz=UTC)

    def is_process_error(self, exc):
        return False

    def is_timeout_error(self, exc):
        return False


class DummyRuntimeApp:
    app_name = "dummy"


def test_runtime_state_reset():
    state = AppRuntimeState(process=object(), pid=42, create_time=1.0)
    state.reset()
    assert state.process is None
    assert state.pid is None
    assert state.create_time is None


def test_runtime_service_is_running_false_when_no_process_found():
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=None))
    assert service.is_running(Path("none"), DummyRuntimeApp()) is False


def test_runtime_service_process_info_falls_back_when_no_process_cached():
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=None))
    result = service.process_info(DummyRuntimeApp())
    assert result["is_running"] is False
    assert result["last_seen"] is None


def test_runtime_service_close_stops_running_process():
    process = DummyProcess()
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=process))
    app = DummyRuntimeApp()

    assert service.is_running(Path("app"), app) is True
    assert service.close(Path("app"), app, timeout=0.1) is True
    assert service.is_running(Path("app"), app) is False
