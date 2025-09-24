import sys

import pytest

from process_inspector.servicecontrol import Service

# pytestmark = pytest.mark.skipif(
#     sys.platform == "darwin", reason="Skipping as requires sudo on macOS"
# )


@pytest.fixture
def app():
    if sys.platform == "win32":
        return Service("Spooler")
    # return Service("teamviewerd.service")  # systemctl
    return Service("xapp_monitor")  # supervisorctl


def test_service_start(app):
    assert app.start() is True


def test_service_is_running(app):
    app.start()
    assert app.is_running() is True


def test_service_stop(app):
    assert app.stop() is True


def test_service_restart(app):
    assert app.restart() is True


def test_service_status(app):
    status = app.status()
    assert isinstance(status, str)
    assert status != "--"


def test_service_invalid():
    if sys.platform == "win32":
        svc = Service("InvalidServiceName")
    else:
        svc = Service("invalid-service-name")
    assert svc.start() is False
    assert svc.stop() is False
    assert svc.restart() is False
    assert svc.is_running() is False
    assert svc.status() == "ERROR"
