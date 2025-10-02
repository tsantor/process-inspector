import logging
import re
import shlex
import subprocess
import time

from .interface import AppInterface

logger = logging.getLogger(__name__)


class App(AppInterface):
    """Basic control of a Mac App using Popen and psutil."""

    def open(self) -> bool:
        """
        The `open` command is the standard way to launch .app bundles via CLI.
        """
        if self.is_running():
            return True

        # Use the 'open' command to launch the .app bundle
        try:
            cmd = ["open", str(self.app_path)]
            proc = subprocess.Popen(cmd)  # noqa: S603
            proc.wait(timeout=1.0)
        except FileNotFoundError:
            logger.exception("App path not found: %s", self.app_path)
            return False
        except Exception:
            logger.exception("Failed to start app: %s", self.app_name)
            return False

        # Wait for process to start so we can get its PID
        start_time = time.time()
        timeout = 10
        while not self.is_running():
            if time.time() - start_time > timeout:
                logger.warnning("Timed out waiting for app to start: %s", self.app_name)
                return False
            time.sleep(0.1)

        return True

    def get_version(self) -> str:
        """
        Get version using mdls (Metadata List), which is reliable and
        doesn't use AppleScript.
        """
        cmd = f'mdls -name kMDItemVersion "{self.app_path}"'
        proc = subprocess.run(  # noqa: S603
            shlex.split(cmd), check=False, capture_output=True, text=True
        )
        result = proc.stdout.strip()
        regex = r"(\d{1,}\.?)+"
        matches = re.search(regex, result)
        return matches[0] if matches else "--"
