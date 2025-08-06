"""Bystronic OPC UA Client Library.

A Python library for connecting to and interacting with Bystronic laser cutting 
machines via OPC UA protocol.
"""

from .client import BystronicClient
from .monitor import MachineMonitor
from .data_types import JobInfo, PlanInfo, PartInfo, RunInfo, MachineStatus
from .exceptions import BystronicOPCError, ConnectionError, DataError

__version__ = "0.1.0"
__author__ = "Daniel Risto"
__email__ = "daniel@risto.de"

__all__ = [
    "BystronicClient",
    "MachineMonitor", 
    "JobInfo",
    "PlanInfo",
    "PartInfo",
    "RunInfo",
    "MachineStatus",
    "BystronicOPCError",
    "ConnectionError",
    "DataError",
]