import sys

import pytest

from process_inspector.taskcontrol import ScheduledTask

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="Only Windows supported for Scheduled Tasks"
)


@pytest.fixture
def scheduled_task():
    """Fixture to create a ScheduledTask instance."""
    return ScheduledTask(name="Start Xapp Monitor")


@pytest.fixture
def nonexistent_scheduled_task():
    """Fixture to create a ScheduledTask instance."""
    return ScheduledTask(name="Nonexistent Task")


def test_status(scheduled_task):
    """Test the _get_task_status method."""
    status = scheduled_task.status()
    assert status in ["RUNNING", "READY"]


def test_nonexistent_status(nonexistent_scheduled_task):
    status = nonexistent_scheduled_task.status()
    assert status == "NOT FOUND"


def test_is_running(scheduled_task):
    assert scheduled_task.is_running() is False


def test_start(scheduled_task):
    assert scheduled_task.start() is True


def test_stop(scheduled_task):
    assert scheduled_task.stop() is True


def test_restart(scheduled_task):
    assert scheduled_task.restart() is True


def test_as_dict(scheduled_task):
    task_dict = scheduled_task.as_dict()
    assert isinstance(task_dict, dict)

    expected_keys = [
        "name",
        "status",
        "is_running",
    ]
    missing_keys = [key for key in expected_keys if key not in task_dict]
    assert not missing_keys, f"Missing keys: {missing_keys}"
