import sys
from pathlib import Path

import pytest

from process_inspector.appcontrol import NativeApp

pytestmark = pytest.mark.skipif(
    sys.platform == "linux", reason="Linux not supported yet"
)


@pytest.fixture
def app():
    if sys.platform == "win32":
        return NativeApp(
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
        )

    return NativeApp(Path("/Applications/Safari.app"))


def test_native_app_open(app):
    assert app.open() is True
    assert app.close() is True


def test_native_app_is_running(app):
    assert app.open() is True
    assert app.is_running() is True
    assert app.close() is True


def test_native_app_close(app):
    assert app.open() is True
    assert app.close() is True


def test_native_app_version(app):
    assert app.get_version() is not None


def test_to_json(app):
    assert isinstance(app.to_json(), str)
    expected_keys = ["exe", "name", "path"]
    assert all(key in app.to_json() for key in expected_keys)


def test_process_info(app):
    assert app.open() is True
    assert app.is_running() is True
    proc_info = app.process_info()
    assert isinstance(proc_info, dict)
    expected_keys = ["pid", "uptime", "uptime_str"]
    assert all(key in proc_info for key in expected_keys)
    assert app.close() is True
