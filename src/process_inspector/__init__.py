import logging

from .appcontrol import NativeApp
from .oscontrol import OperatingSystem
from .scriptcontrol import Script
from .servicecontrol import Service
from .taskcontrol import ScheduledTask
from .teamviewer import Teamviewer

__version__ = "0.2.2"

__all__ = [
    "NativeApp",
    "OperatingSystem",
    "ScheduledTask",
    "Script",
    "Service",
    "Teamviewer",
]

# Basic logger setup; users of this package can configure logging as needed
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
