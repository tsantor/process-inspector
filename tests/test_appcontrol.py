import contextlib
import json
import sys
import time
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


@pytest.fixture(autouse=False)
def ensure_app_closed(app):
    # Ensure the app is closed before each test
    with contextlib.suppress(Exception):
        app.close()
    yield
    # Ensure the app is closed after each test
    with contextlib.suppress(Exception):
        app.close()


def test_app_open(app):
    assert app.open() is True
    timeout = 10
    start = time.time()
    while not app.is_running():
        if time.time() - start > timeout:
            pytest.fail("App did not start within timeout")
        time.sleep(1)
    assert app.close() is True


def test_app_is_running(app):
    assert app.open() is True
    timeout = 10
    start = time.time()
    while not app.is_running():
        if time.time() - start > timeout:
            pytest.fail("App did not start within timeout")
        time.sleep(1)
    assert app.is_running() is True
    assert app.close() is True


def test_app_close(app):
    assert app.open() is True
    timeout = 10
    start = time.time()
    while not app.is_running():
        if time.time() - start > timeout:
            pytest.fail("App did not start within timeout")
        time.sleep(1)
    assert app.close() is True


def test_close_when_app_not_running(app):
    assert app.close() is True


def test_app_version(app):
    assert app.get_version() is not None


def test_to_dict(app):
    app_dict = app.to_dict()
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
    assert isinstance(app_dict["install_date"], str)
    assert isinstance(app_dict["install_date_short"], str)
    assert isinstance(app_dict["version"], str)
    assert isinstance(app_dict["is_installed"], bool)
    assert app_dict["is_installed"] is True
    assert app_dict["exe"] == app.app_exe
    assert app_dict["name"] == app.app_name
    assert app_dict["path"] == str(app.app_path)


def test_process_info(app):
    assert app.open() is True
    timeout = 10
    start = time.time()
    while not app.is_running():
        if time.time() - start > timeout:
            pytest.fail("App did not start within timeout")
        time.sleep(1)
    assert app.is_running() is True
    proc_info = app.process_info()
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
    assert app.close() is True
    assert isinstance(proc_info["pid"], int)
    assert isinstance(proc_info["status"], str)
    assert isinstance(proc_info["mem_usage_percent"], str)
    assert isinstance(proc_info["mem_usage"], str)
    assert isinstance(proc_info["vmem_usage"], str)
    assert isinstance(proc_info["proc_usage"], str)
    assert isinstance(proc_info["uptime_seconds"], int)
    assert isinstance(proc_info["uptime"], str)


def test_to_dict_is_serializable(app):
    app_dict = app.to_dict()
    serialized = json.dumps(app_dict)
    assert isinstance(serialized, str)


def test_process_info_is_serializable(app):
    assert app.open() is True
    timeout = 10
    start = time.time()
    while not app.is_running():
        if time.time() - start > timeout:
            pytest.fail("App did not start within timeout")
        time.sleep(1)
    assert app.is_running() is True
    proc_info = app.process_info()
    serialized = json.dumps(proc_info)
    assert isinstance(serialized, str)
    assert app.close() is True
