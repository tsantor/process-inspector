import sys

import pytest

from process_inspector.servicecontrol import Service


@pytest.fixture
def app():
    if sys.platform == "win32":
        return Service("Spooler")
    return Service("process_inspector")


def test_service_start(app):
    assert app.start() is True


def test_service_is_running(app):
    app.start()
    assert app.is_running() is True


def test_service_stop(app):
    assert app.stop() is True


def test_service_restart(app):
    assert app.restart() is True
