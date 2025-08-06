"""Data type definitions for Bystronic OPC UA data structures."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


@dataclass
class JobInfo:
    """Information about a cutting job."""
    
    guid: UUID
    name: str
    file_path: str
    created_at: Optional[datetime] = None
    status: Optional[str] = None


@dataclass
class PlanInfo:
    """Information about a cutting plan."""
    
    job_guid: UUID
    plan_guid: UUID
    name: str
    size_x: float
    size_y: float
    material_thickness: float
    total_runs: int
    total_parts: int
    plan_state: int
    estimated_cut_time: float
    parameter_file: Optional[str] = None


@dataclass
class PartInfo:
    """Information about a part in a job."""
    
    job_guid: UUID
    part_id: int
    part_ref_ids: str
    name: str
    description: str
    quantity: int
    order_info: str
    user_info_1: Optional[str] = None
    user_info_2: Optional[str] = None


@dataclass
class RunInfo:
    """Information about a cutting run."""
    
    run_guid: UUID
    job_guid: UUID
    actual_cut_time: float
    actual_stop_time: float
    actual_wait_time: float
    cut_start_time: Optional[datetime] = None
    cut_end_time: Optional[datetime] = None


@dataclass
class LaserParameters:
    """Current laser parameters."""
    
    current_laser_power: float
    gas_channel: int
    gas_pressure: float
    laser_power_deviation: float
    laser_power_setpoint: float
    process_operation_mode: int


@dataclass
class MachineStatus:
    """Overall machine status information."""
    
    machine_url: str
    is_connected: bool
    current_job: Optional[JobInfo] = None
    laser_parameters: Optional[LaserParameters] = None
    last_update: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class HistoryQuery:
    """Parameters for historical data queries."""
    
    from_timestamp: datetime
    to_timestamp: datetime
    page: int = 1
    page_size: int = 100