import logging

from .implementations import SupervisorCtl

logger = logging.getLogger(__name__)


class Service(SupervisorCtl):
    """macOS Supervisor Control"""
