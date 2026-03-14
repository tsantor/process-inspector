from __future__ import annotations

from datetime import UTC
from datetime import datetime

from process_inspector.servicecontrol.application.service import ServiceRuntimeService
from process_inspector.servicecontrol.domain.entities import ServiceRuntimeState
from process_inspector.servicecontrol.domain.value_objects import ServiceIdentity


class DummyProcess:
    def __init__(self):
        self.pid = 321


class DummyRuntimePort:
    def __init__(self, process=None):
        self.process = process

    def load_process(self, pid):
        return self.process

    def get_process_info(self, process):
        return {"pid": 321, "status": "RUNNING"}

    def now_utc(self):
        return datetime.now(tz=UTC)


class DummyService:
    name = "dummy"


def test_service_identity_name():
    identity = ServiceIdentity(name="svc")
    assert identity.name == "svc"


def test_service_runtime_state_reset():
    state = ServiceRuntimeState(process=object(), pid=7)
    state.reset()
    assert state.process is None
    assert state.pid is None


def test_sync_process_cache_with_missing_pid():
    service = ServiceRuntimeService(runtime_port=DummyRuntimePort(process=None))
    result = service.sync_process_cache(DummyService(), current_pid=None)
    assert result is None
    assert service.pid is None


def test_evaluate_running_true_sets_last_seen():
    runtime = ServiceRuntimeService(
        runtime_port=DummyRuntimePort(process=DummyProcess())
    )
    running = runtime.evaluate_running(
        DummyService(), process=DummyProcess(), status_value="RUNNING"
    )
    assert running is True
    assert runtime.get_last_seen_str() is not None


def test_process_info_fallback_when_no_process():
    runtime = ServiceRuntimeService(runtime_port=DummyRuntimePort(process=None))
    assert runtime.process_info(DummyService()) == {
        "is_running": False,
        "last_seen": None,
    }
