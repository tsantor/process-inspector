import logging
import subprocess
import time

logger = logging.getLogger(__name__)


def _run_powershell_command(
    command: list[str], check: bool = True
) -> subprocess.CompletedProcess | None:
    """Executes a PowerShell command and returns the result."""
    full_command = ["powershell", "-Command"] + command
    try:
        # logger.debug("Executing PowerShell: %s", " ".join(full_command))
        return subprocess.run(  # noqa: S603
            full_command,
            capture_output=True,
            text=True,
            check=check,
            encoding="utf-8",
            timeout=10,
        )
    except subprocess.CalledProcessError as e:
        logger.error(  # noqa: TRY400
            "PowerShell command failed with exit code %d: %s\nStderr: %s",
            e.returncode,
            e.cmd,
            e.stderr.strip(),
        )
        return None
    except FileNotFoundError:
        logger.error("PowerShell executable not found.")  # noqa: TRY400
        return None
    except Exception:
        logger.exception("An unexpected error occurred while running PowerShell")
        return None


class ScheduledTask:
    """
    Control for a Windows Scheduled Task using PowerShell commands.
    """

    def __init__(self, name: str):
        self.name = name

        if not self._task_exists():
            logger.warning("Task does not exist: '%s'", name)

    def _task_exists(self) -> bool:
        return self._get_task_status() in ["READY", "RUNNING"]

    def _get_task_status(self) -> str:
        """Helper to fetch the current status of the scheduled task."""
        # Use Get-ScheduledTask to fetch the state
        command = ["(Get-ScheduledTask", "-TaskName", f"'{self.name}'", ").State"]
        result = _run_powershell_command(command, check=False)

        # If the task is not found
        if result and "No MSFT_ScheduledTask objects found" in result.stderr:
            return "NOT FOUND"

        if result and result.returncode == 0:
            return result.stdout.strip().upper()

        logger.warning(
            "Could not determine task status for '%s'. Output: %s",
            self.name,
            result.stderr if result else "None",
        )
        return "UNKNOWN"

    def is_running(self) -> bool:
        """Check if the Task Scheduler reports the task as 'Running'."""
        status = self.status()
        return status == "RUNNING"

    def start(self) -> bool:
        """
        Starts the scheduled task immediately using 'Start-ScheduledTask'.
        """
        logger.info("Starting Task Scheduler Task: %s", self.name)
        command = ["Start-ScheduledTask", "-TaskName", f"'{self.name}'"]
        result = _run_powershell_command(command)
        return result is not None and result.returncode == 0

    def stop(self) -> bool:
        """
        Stops all running instances of the scheduled task using 'Stop-ScheduledTask'.
        """
        logger.info("Stopping Task Scheduler Task: %s", self.name)
        # Stop-ScheduledTask will terminate any running processes started by the task.
        command = ["Stop-ScheduledTask", "-TaskName", f"'{self.name}'"]
        result = _run_powershell_command(command)
        return result is not None and result.returncode == 0

    def restart(self) -> bool:
        """
        Stops and then starts the scheduled task. Note: A task may not be
        stoppable if it's already finished, or its child process is misbehaving.
        """
        logger.info("Restarting Task Scheduler Task: %s", self.name)
        # Attempt to stop first. Continue even if stop fails, as it might have finished.
        self.stop()

        # Give a small delay for processes to fully terminate
        time.sleep(1)

        return self.start()

    def status(self) -> str:
        """
        Returns the reported state of the scheduled task
        (e.g., 'READY', 'RUNNING', 'DISABLED').
        """
        return self._get_task_status()

    def __repr__(self):
        return f"ScheduledTask('{self.name}')"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "is_running": self.is_running(),
            "status": self.status(),
        }
