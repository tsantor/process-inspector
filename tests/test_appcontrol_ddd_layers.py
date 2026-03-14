from __future__ import annotations

from datetime import UTC
from datetime import datetime
from pathlib import Path

from process_inspector.appcontrol.application.service import AppRuntimeService
from process_inspector.appcontrol.domain.entities import AppRuntimeState
from process_inspector.appcontrol.domain.value_objects import AppIdentity


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


class DummyApp:
    app_name = "dummy"


def test_app_identity_from_path():
    identity = AppIdentity.from_path(Path("/Applications/Safari.app"))
    assert identity.app_exe == "Safari.app"
    assert identity.app_name == "Safari"


def test_runtime_state_reset():
    state = AppRuntimeState(process=object(), pid=42, create_time=1.0)
    state.reset()
    assert state.process is None
    assert state.pid is None
    assert state.create_time is None


def test_service_is_running_false_when_no_process_found():
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=None))
    assert service.is_running(Path("none"), DummyApp()) is False


def test_service_process_info_falls_back_when_no_process_cached():
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=None))
    result = service.process_info(DummyApp())
    assert result["is_running"] is False
    assert result["last_seen"] is None


def test_service_close_stops_running_process():
    process = DummyProcess()
    service = AppRuntimeService(runtime_port=DummyRuntimePort(process=process))
    app = DummyApp()

    assert service.is_running(Path("app"), app) is True
    assert service.close(Path("app"), app, timeout=0.1) is True
    assert service.is_running(Path("app"), app) is False
