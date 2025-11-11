import logging
import re
import shlex
import subprocess
import time

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Mac App using Popen and psutil."""

    def open(self, timeout: float = 3.0) -> bool:
        """Open app and wait to grab its PID if possible."""
        if self.is_running():
            return True

        # Use the 'open' command to launch the .app bundle
        try:
            cmd = ["open", str(self.app_path)]
            subprocess.Popen(cmd)  # noqa: S603
        except FileNotFoundError:
            logger.exception("App path not found: %s", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app: %s", self.app_name)
            return False

        # Wait for process to start so we can get its PID
        start_time = time.time()
        while not self.is_running():
            if time.time() - start_time > timeout:
                logger.warning("Timed out waiting for app to start: %s", self.app_name)
                return False
            time.sleep(0.1)

        return True

    def close(self, timeout: float = 3.0) -> bool:
        """Close the running app we launched (terminate -> kill) and wait."""
        applescript_command = f'tell application "{self.app_name}" to quit'
        try:
            subprocess.run(["osascript", "-e", applescript_command], check=True)  # noqa: S603, S607
            logger.debug("'%s' sent clean quit signal.", self.app_name)

            # Wait a moment for the quit to complete
            start_time = time.time()
            while not self.is_running():
                if time.time() - start_time > timeout:
                    logger.warning("Timed out waiting for '%s' to stop", self.app_name)
                    return super().close()
                time.sleep(0.1)

            elapsed = time.time() - start_time
            logger.debug(
                "'%s' quit successfully in %.2f seconds.",
                self.app_name,
                elapsed,
            )

        except subprocess.CalledProcessError as e:
            logger.error(  # noqa: TRY400
                "Failed to send quit signal to '%s' via AppleScript. %s",
                self.app_name,
                e,
            )
        except FileNotFoundError:
            logger.error(  # noqa: TRY400
                "osascript utility not found. Ensure you are on macOS."
            )

    def get_version(self) -> str:
        """
        Get version using mdls (Metadata List), which is reliable and
        doesn't use AppleScript.
        """
        cmd = f'mdls -name kMDItemVersion "{self.app_path}"'
        # logger.debug("Execute command: %s", cmd)
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
