import subprocess

from process_inspector.appcontrol.interface import AppInterface


def run_script(path: str) -> int | None:
    try:
        result = subprocess.run(  # noqa: S603
            [path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return None


class Script(AppInterface):
    """Basic control of a Script which launches a child process."""

    def is_running(self) -> bool:
        """Check if the script is running."""
        msg = "is_running not implemented for Windows scripts."
        raise NotImplementedError(msg)

    def open(self):
        """Open the application."""
        msg = "open not implemented for Windows scripts."
        raise NotImplementedError(msg)

    def get_version(self) -> str:
        return "--"
