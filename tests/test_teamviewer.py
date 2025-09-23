import contextlib
import json
import time
from pathlib import Path

import pytest

from process_inspector.teamviewer import Teamviewer
from process_inspector.teamviewer import get_teamviewer_info
from process_inspector.teamviewer import get_teamviewer_path
from process_inspector.teamviewer import is_teamviewer_installed

pytestmark = pytest.mark.skipif(
    not is_teamviewer_installed(), reason="TeamViewer is not installed"
)


@pytest.fixture
def teamviewer():
    return Teamviewer()


@pytest.fixture(autouse=False)
def ensure_app_closed(teamviewer):
    # Ensure the app is closed before each test
    with contextlib.suppress(Exception):
        teamviewer.close()
    yield
    # Ensure the app is closed after each test
    with contextlib.suppress(Exception):
        teamviewer.close()


def test_get_teamviewer_info():
    info = get_teamviewer_info()
    assert all(x in info for x in ["id", "version", "path", "is_installed"])


def test_get_teamviewer_info_is_serializable(teamviewer):
    info = get_teamviewer_info()
    serialized = json.dumps(info)
    assert isinstance(serialized, str)


def test_get_teamviewer_path():
    path = get_teamviewer_path()
    assert isinstance(path, Path)


def test_teamviewer_open(teamviewer):
    assert teamviewer.open() is True


def test_teamviewer_is_running(teamviewer):
    assert teamviewer.open() is True
    time.sleep(1)  # Give it a moment to start
    assert teamviewer.is_running() is True


@pytest.mark.skip(reason="We don't want to close TeamViewer during tests")
def test_teamviewer_close(teamviewer):
    assert teamviewer.close() is True
