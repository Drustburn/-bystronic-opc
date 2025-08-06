# API Reference

## Core Classes

### BystronicClient

Main client class for connecting to individual Bystronic machines.

```python
from bystronic_opc import BystronicClient

client = BystronicClient("opc.tcp://192.168.1.100:56000")
```

#### Constructor

```python
BystronicClient(url: str, timeout: int = 10)
```

**Parameters:**
- `url`: OPC UA server URL
- `timeout`: Connection timeout in seconds (default: 10)

#### Methods

##### async connect()
Establish connection to the OPC UA server.

```python
await client.connect()
```

**Raises:**
- `ConnectionError`: If connection fails

##### async disconnect()
Close the connection to the OPC UA server.

```python
await client.disconnect()
```

##### async get_current_job()
Get information about the currently active job.

```python
job = await client.get_current_job()
if job:
    print(f"Current job: {job.name}")
```

**Returns:**
- `JobInfo | None`: Current job information or None if no job is active

##### async get_job_info(job_guid: UUID)
Get detailed information about a specific job.

```python
from uuid import UUID
job_info = await client.get_job_info(UUID("a99ae277-7391-4326-ae6f-901f62c524a3"))
```

**Parameters:**
- `job_guid`: UUID of the job

**Returns:**
- `Dict[str, Any] | None`: Job information dictionary

##### async get_plan_info(job_guid: UUID)
Get plan/program information for a job.

```python
plan_info = await client.get_plan_info(job_guid)
```

**Parameters:**
- `job_guid`: UUID of the job

**Returns:**
- `Dict[str, Any] | None`: Plan information dictionary

##### async get_part_info(job_guid: UUID)
Get part information for a job.

```python
part_info = await client.get_part_info(job_guid)
```

**Parameters:**
- `job_guid`: UUID of the job

**Returns:**
- `Dict[str, Any] | None`: Part information dictionary

##### async get_run_history(from_timestamp, to_timestamp, page=1, page_size=100)
Get historical run data within a time range.

```python
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(days=1)
runs = await client.get_run_history(start_time, end_time)
```

**Parameters:**
- `from_timestamp`: Start time (datetime)
- `to_timestamp`: End time (datetime)  
- `page`: Page number (default: 1)
- `page_size`: Number of entries per page (default: 100)

**Returns:**
- `List[Dict[str, Any]]`: List of run history entries

##### async get_laser_parameters()
Get current laser parameter values.

```python
laser_params = await client.get_laser_parameters()
print(f"Laser power: {laser_params.current_laser_power}")
```

**Returns:**
- `LaserParameters`: Current laser parameter values

##### async get_screen_image()
Capture the machine's screen image.

```python
image_data = await client.get_screen_image()
with open("screen.png", "wb") as f:
    f.write(image_data)
```

**Returns:**
- `bytes`: PNG image data

##### async get_machine_status()
Get comprehensive machine status information.

```python
status = await client.get_machine_status()
print(f"Connected: {status.is_connected}")
```

**Returns:**
- `MachineStatus`: Complete machine status

### MachineMonitor

Monitor multiple machines simultaneously.

```python
from bystronic_opc import MachineMonitor

machines = {
    "Machine_1": "opc.tcp://192.168.1.101:56000",
    "Machine_2": "opc.tcp://192.168.1.102:56000"
}

monitor = MachineMonitor(machines, update_interval=30)
```

#### Constructor

```python
MachineMonitor(
    machines: Dict[str, str],
    update_interval: int = 30,
    retry_attempts: int = 3
)
```

**Parameters:**
- `machines`: Dictionary mapping machine names to OPC UA URLs
- `update_interval`: Update frequency in seconds (default: 30)
- `retry_attempts`: Number of retry attempts for failed connections (default: 3)

#### Methods

##### async start_monitoring()
Start monitoring all configured machines.

```python
await monitor.start_monitoring()
```

##### async stop_monitoring()
Stop monitoring and disconnect from all machines.

```python
await monitor.stop_monitoring()
```

##### get_machine_status(machine_name: str)
Get status of a specific machine.

```python
status = monitor.get_machine_status("Machine_1")
```

**Parameters:**
- `machine_name`: Name of the machine

**Returns:**
- `MachineStatus | None`: Machine status or None if not found

##### get_all_machine_status()
Get status of all machines.

```python
all_status = monitor.get_all_machine_status()
```

**Returns:**
- `Dict[str, MachineStatus]`: Dictionary mapping machine names to their status

##### get_connected_machines()
Get list of currently connected machines.

```python
connected = monitor.get_connected_machines()
```

**Returns:**
- `List[str]`: List of connected machine names

## Data Types

### JobInfo

```python
@dataclass
class JobInfo:
    guid: UUID
    name: str
    file_path: str
    created_at: Optional[datetime] = None
    status: Optional[str] = None
```

### PlanInfo

```python
@dataclass
class PlanInfo:
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
```

### PartInfo

```python
@dataclass
class PartInfo:
    job_guid: UUID
    part_id: int
    part_ref_ids: str
    name: str
    description: str
    quantity: int
    order_info: str
    user_info_1: Optional[str] = None
    user_info_2: Optional[str] = None
```

### LaserParameters

```python
@dataclass
class LaserParameters:
    current_laser_power: float
    gas_channel: int
    gas_pressure: float
    laser_power_deviation: float
    laser_power_setpoint: float
    process_operation_mode: int
```

### MachineStatus

```python
@dataclass
class MachineStatus:
    machine_url: str
    is_connected: bool
    current_job: Optional[JobInfo] = None
    laser_parameters: Optional[LaserParameters] = None
    last_update: Optional[datetime] = None
    error_message: Optional[str] = None
```

## Exceptions

### BystronicOPCError
Base exception class for all library-specific errors.

### ConnectionError
Raised when OPC UA connection fails.

### DataError
Raised when data parsing or processing fails.

### MethodCallError
Raised when OPC UA method calls fail.

### ConfigurationError
Raised when configuration is invalid.

## Context Managers

Both `BystronicClient` and `MachineMonitor` support async context managers:

```python
# Single client
async with BystronicClient("opc.tcp://machine:56000") as client:
    status = await client.get_machine_status()

# Monitor
async with MachineMonitor(machines) as monitor:
    # Monitoring starts automatically
    status = monitor.get_all_machine_status()
    # Monitoring stops automatically on exit
```