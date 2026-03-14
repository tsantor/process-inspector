from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING
from typing import Any

from process_inspector.appcontrol.domain.entities import AppRuntimeState

if TYPE_CHECKING:
    from pathlib import Path

    from process_inspector.appcontrol.application.ports import ProcessRuntimePort

logger = logging.getLogger(__name__)


class AppRuntimeService:
    """Application service orchestrating app runtime state and process lifecycle."""

    def __init__(
        self,
        runtime_port: ProcessRuntimePort,
        state_change_callback=None,
        *,
        pid_create_time_tolerance: float = 0.001,
    ):
        self._runtime_port = runtime_port
        self._state = AppRuntimeState()
        self._on_state_change_cb = state_change_callback
        self._pid_create_time_tolerance = pid_create_time_tolerance

    @property
    def pid(self) -> int | None:
        return self._state.pid

    @property
    def last_seen(self):
        return self._state.last_seen

    def reset_cache(self) -> None:
        self._state.reset()

    def update_running_state(self, app: Any, *, is_running: bool) -> None:
        if self._state.last_running_state != is_running:
            if self._on_state_change_cb:
                self._on_state_change_cb(app=app, is_running=is_running)
            self._state.last_running_state = is_running

    def is_running(self, app_path: Path, app: Any) -> bool:
        """Check if the tracked app instance is running."""
        try:
            if self._state.process is None:
                if self._state.pid is None:
                    proc = self._runtime_port.find_process(app_path)
                    if not proc:
                        self.update_running_state(app, is_running=False)
                        return False
                else:
                    proc = self._runtime_port.load_process(self._state.pid)

                self._state.process = proc
                self._state.pid = proc.pid
                self._state.create_time = self._runtime_port.process_create_time(proc)

            process = self._state.process
            if process is None:
                self.update_running_state(app, is_running=False)
                return False

            if (
                not self._runtime_port.is_process_running(process)
                or self._runtime_port.is_process_zombie(process)
                or abs(
                    self._runtime_port.process_create_time(process)
                    - float(self._state.create_time)
                )
                > self._pid_create_time_tolerance
            ):
                logger.debug("Process %s no longer valid. Resetting cache.", app)
                self.reset_cache()
                self.update_running_state(app, is_running=False)
                return False

            self._state.mark_seen(self._runtime_port.now_utc())
            self.update_running_state(app, is_running=True)
            return True

        except Exception as exc:
            if self._runtime_port.is_process_error(exc):
                logger.error("Process %s error", app)  # noqa: TRY400
                self.reset_cache()
                self.update_running_state(app, is_running=False)
                return False
            raise
        except OSError as e:
            logger.error("Error checking process state for %s: %s", app, e)  # noqa: TRY400
            self.update_running_state(app, is_running=False)
            return False

    def close(self, app_path: Path, app: Any, *, timeout: float = 5.0) -> bool:  # noqa: C901
        if not self.is_running(app_path, app):
            self.reset_cache()
            self.update_running_state(app, is_running=False)
            return True

        start_time = time.perf_counter()

        try:
            process = self._state.process or self._runtime_port.load_process(
                self._state.pid
            )
        except Exception as exc:
            if self._runtime_port.is_process_error(exc):
                self.reset_cache()
                self.update_running_state(app, is_running=False)
                return True
            raise

        try:
            self._runtime_port.terminate_process(process)
            self._runtime_port.wait_process(process, timeout=5)
            logger.debug("Terminated process %s", app)
        except Exception as exc:
            if not self._runtime_port.is_timeout_error(exc):
                if self._runtime_port.is_process_error(exc):
                    logger.debug("Process %s already exited during termination", app)
                    return True
                raise
            try:
                self._runtime_port.kill_process(process)
                self._runtime_port.wait_process(process, timeout=3)
                logger.debug("Killed process %s", app)
            except Exception as inner_exc:
                if self._runtime_port.is_process_error(
                    inner_exc
                ) or self._runtime_port.is_timeout_error(inner_exc):
                    logger.warning("Failed to kill process %s", app)
                else:
                    raise

        while self.is_running(app_path, app):
            if time.perf_counter() - start_time > timeout:
                logger.warning(
                    "Timed out (%s secs) waiting for %s to close",
                    timeout,
                    app,
                )
            time.sleep(0.1)

        elapsed = time.perf_counter() - start_time
        logger.debug(
            "App '%s' quit successfully in %.3f seconds.", app.app_name, elapsed
        )
        self.reset_cache()
        self.update_running_state(app, is_running=False)
        return True

    def get_last_seen_str(self) -> str | None:
        if self._state.last_seen is None:
            return None
        return self._state.last_seen.isoformat()

    def process_info(self, app: Any) -> dict:
        process = self._state.process
        if process:
            try:
                return {
                    **self._runtime_port.get_process_info(process),
                    "last_seen": self.get_last_seen_str(),
                }
            except Exception as exc:
                if self._runtime_port.is_process_error(exc):
                    logger.warning("Process %s no longer exists.", app)
                    self.reset_cache()
                    self.update_running_state(app, is_running=False)
                else:
                    raise

        return {
            "is_running": False,
            "last_seen": self.get_last_seen_str(),
        }

    def install_date_human_short(self, install_date) -> str | None:
        if install_date is None:
            return None
        return self._runtime_port.human_datetime_short(install_date)
