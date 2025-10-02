import logging

from .appcontrol import NativeApp  # noqa: F401
from .oscontrol import OperatingSystem  # noqa: F401
from .servicecontrol import Service  # noqa: F401
from .teamviewer import Teamviewer  # noqa: F401

# Basic logger setup; users of this package can configure logging as needed
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

__version__ = "0.1.6"
