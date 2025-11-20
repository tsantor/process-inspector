import json
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)


# --- Optimized Helper Function ---
def _run_powershell_command(
    command: list[str], check: bool = True
) -> subprocess.CompletedProcess | None:
    """
    Executes a PowerShell command with optimizations (-NoProfile, -NonInteractive)
    and returns the result.
    """
    command_str = " ".join(command)
    full_command = [
        "powershell",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        command_str,
    ]
    try:
        result = subprocess.run(  # noqa: S603
            full_command,
            capture_output=True,
            text=True,
            check=check,
            encoding="utf-8",
            timeout=20,
        )
        if result.returncode != 0:
            logger.error(
                "PowerShell command failed with return code %d. Raw STDOUT: %s",
                result.returncode,
                result.stdout.strip(),
            )

        return result

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
    Control for a Windows Scheduled Task using optimized PowerShell commands.
    Retrieves status, last run time, and result with a single, efficient PowerShell call.
    """

    TASK_STATE_MAP = {
        0: "UNKNOWN",
        1: "DISABLED",
        2: "QUEUED",
        3: "READY",
        4: "RUNNING",
    }

    def __init__(self, name: str, state_change_callback=None):
        self.name = name
        self._on_state_change_cb = state_change_callback
        self._last_running_state: bool | None = None
        self._last_run_time: str | None = None
        self._task_data: dict | None = None  # Cache for consolidated data

        # Initial data fetch using the efficient method
        self._fetch_task_data()
        if not self._task_exists():
            logger.warning("Task does not exist: '%s'", name)

    def _fetch_task_data(self) -> None:
        """
        Consolidates status data retrieval into a single PowerShell call.
        PowerShell now returns the raw integer State index, which is mapped in Python.
        """

        # Cleaner PowerShell command: returns the raw State index (0-4).
        command = [
            f"Get-ScheduledTask -TaskName '{self.name}' -ErrorAction Stop |",
            # We explicitly fetch the State integer, LastTaskResult, and format LastRunTime.
            "Select-Object -Property TaskName, State, @{Name='LastTaskResult'; Expression={(Get-ScheduledTaskInfo $_).LastTaskResult}}, @{Name='LastRunTime'; Expression={(Get-ScheduledTaskInfo $_).LastRunTime.ToString('o')}} |",
            "ConvertTo-Json -Compress",
        ]

        result = _run_powershell_command(command, check=False)
        self._task_data = None  # Reset cache

        raw_output = result.stdout.strip() if result else "No Result"

        if result and result.returncode == 0 and raw_output:
            # logger.debug(result)
            try:
                self._task_data = json.loads(raw_output)
            except json.JSONDecodeError:
                logger.error(  # noqa: TRY400
                    "Failed to decode JSON output for task '%s'. Raw Output: %s",
                    self.name,
                    raw_output,
                )
        elif result and "No MSFT_ScheduledTask objects found" in result.stderr:
            # Task not found
            logger.warning("Scheduled Task '%s' not found")
        else:
            logger.warning(
                "Could not fetch task data for '%s'. Task may not exist or PowerShell failed. Raw STDOUT: %s",
                self.name,
                raw_output,
            )

    def _task_exists(self) -> bool:
        """Checks if task data was successfully fetched."""
        return self._task_data is not None

    def _get_task_status(self) -> str:
        """Helper to fetch the current status from cached data, mapping the integer index to a string."""
        if not self._task_data:
            return "NOT FOUND"

        # Retrieves the integer index (e.g., 4 for Running)
        state_index = self._task_data.get("State")

        # Use TASK_STATE_MAP to convert the index to a string, defaulting to "UNKNOWN"
        return self.TASK_STATE_MAP.get(state_index, "UNKNOWN")

    def status(self):
        return self._get_task_status()

    def _get_last_run_time(self) -> str | None:
        """
        Fetch the last run time using the ISO 8601 string from PowerShell
        that includes the local system's offset (e.g., -05:00).
        """
        if not self._task_data:
            return None

        last_run_time = self._task_data.get("LastRunTime")
        if not last_run_time or last_run_time.startswith("0001"):
            return None

        try:
            dt_obj_aware = datetime.fromisoformat(last_run_time)
            return dt_obj_aware.astimezone().isoformat(timespec="microseconds")

        except ValueError as e:
            logger.warning(
                "Could not parse LastRunTime '%s' for task '%s'. Error: %s",
                last_run_time,
                self.name,
                e,
            )
            return last_run_time

    def _get_last_run_result(self) -> str | None:
        """Fetch the last run result from the cached data."""
        if not self._task_data:
            return None
        last_run_result = self._task_data.get("LastTaskResult")
        return str(last_run_result) if last_run_result is not None else None

    def _check_state_change(self) -> bool:
        """
        Check if running state has changed and trigger callback if needed.
        Returns True if state changed, False otherwise.
        """
        if not self._task_data:
            return False

        current_running = self._get_task_status() == "RUNNING"

        if self._last_running_state != current_running:
            logger.debug(
                "Scheduled Task '%s' running state changed to: %s",
                self.name,
                current_running,
            )
            if self._on_state_change_cb:
                self._on_state_change_cb(task=self, is_running=current_running)
            self._last_running_state = current_running
            return True

        return False

    def refresh(self) -> None:
        """
        Performs a **data refresh** using the single PowerShell call.
        """
        self._fetch_task_data()

    def is_running(self) -> bool:
        """Check if the Task Scheduler reports the task as 'Running'."""
        # Note: status() returns an already uppercased string from the map.
        return self._get_task_status() == "RUNNING"

    def start(self) -> bool:
        """
        Starts the scheduled task immediately using 'Start-ScheduledTask'.
        Triggers state change callback if running state changes.
        """
        logger.info("Starting Task Scheduler Task: %s", self.name)

        command = [f"Start-ScheduledTask -TaskName '{self.name}'"]
        result = _run_powershell_command(command)
        success = result is not None and result.returncode == 0

        # Refresh data and check for state change
        self._fetch_task_data()
        self._check_state_change()

        return success

    def stop(self) -> bool:
        """
        Stops all running instances of the scheduled task using 'Stop-ScheduledTask'.
        Triggers state change callback if running state changes.
        """
        logger.info("Stopping Task Scheduler Task: %s", self.name)

        command = [f"Stop-ScheduledTask -TaskName '{self.name}'"]
        result = _run_powershell_command(command)
        success = result is not None and result.returncode == 0

        # Refresh data and check for state change
        self._fetch_task_data()
        self._check_state_change()

        return success

    def restart(self) -> bool:
        """
        Stops and then starts the scheduled task.
        Triggers state change callbacks as appropriate.
        """
        logger.info("Restarting Task Scheduler Task: %s", self.name)

        # Stop and check for state change
        if self.stop():
            # Start and check for state change
            return self.start()
        return False

    def __repr__(self):
        return f"ScheduledTask('{self.name}')"

    def as_dict(self) -> dict:
        """Gathers all task information."""
        return {
            "name": self.name,
            "status": self._get_task_status(),
            "is_running": self.is_running(),
            "last_run_time": self._get_last_run_time(),
            "last_run_result": self._get_last_run_result(),
        }
