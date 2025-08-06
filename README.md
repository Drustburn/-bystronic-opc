# Bystronic OPC UA Client

A Python library for connecting to and interacting with Bystronic laser cutting machines via OPC UA protocol. This library provides easy access to machine data, job information, historical data, and real-time monitoring capabilities.

## Features

- **OPC UA Connection Management**: Simplified connection handling for Bystronic machines
- **Job Information**: Retrieve current and historical job data including GUIDs, names, and file paths
- **Plan Information**: Access cutting plan details, material specifications, and parameters
- **Part Information**: Get part quantities, order information, and specifications
- **Run Data**: Monitor cutting times, machine states, and operational statistics
- **Historical Data**: Query historical runs, machine states, and operational data
- **Screen Capture**: Retrieve machine screen images
- **Laser Parameters**: Monitor real-time laser power, gas pressure, and operation modes
- **Web Interface**: Optional Flask-based web dashboard for monitoring and control

## Installation

```bash
pip install bystronic-opc
```

## Quick Start

### Basic Connection

```python
import asyncio
from bystronic_opc import BystronicClient

async def main():
    client = BystronicClient("opc.tcp://192.168.1.100:56000")
    
    # Connect to machine
    await client.connect()
    
    # Get current job information
    job_info = await client.get_current_job()
    print(f"Current Job: {job_info}")
    
    # Get historical run data
    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    run_history = await client.get_run_history(start_time, end_time)
    print(f"Found {len(run_history)} runs")
    
    # Disconnect
    await client.disconnect()

# Run the example
asyncio.run(main())
```

### Monitoring Multiple Machines

```python
from bystronic_opc import MachineMonitor

# Configure multiple machines
machines = {
    "Machine_1": "opc.tcp://192.168.1.101:56000",
    "Machine_2": "opc.tcp://192.168.1.102:56000",
    "Machine_3": "opc.tcp://192.168.1.103:56000"
}

monitor = MachineMonitor(machines)

# Start monitoring (async)
await monitor.start_monitoring()

# Get current status of all machines
status = await monitor.get_all_machine_status()
print(status)
```

### Web Dashboard

```python
from bystronic_opc.web import create_app

# Create Flask app with machine configuration
app = create_app({
    "Machine_1": "opc.tcp://192.168.1.101:56000",
    "Machine_2": "opc.tcp://192.168.1.102:56000"
})

# Run the web interface
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## API Reference

### BystronicClient

Main client class for connecting to individual machines.

#### Methods

- `connect()` - Establish OPC UA connection
- `disconnect()` - Close connection
- `get_current_job()` - Get current job information
- `get_job_info(job_guid)` - Get specific job details
- `get_plan_info(job_guid)` - Get plan/program information  
- `get_part_info(job_guid)` - Get part specifications
- `get_run_info(run_guid)` - Get run statistics
- `get_run_history(start_time, end_time)` - Get historical runs
- `get_machine_state_history(start_time, end_time)` - Get machine states
- `get_laser_parameters()` - Get current laser settings
- `get_screen_image()` - Capture machine screen

### Data Structures

#### JobInfo
```python
{
    "guid": "a99ae277-7391-4326-ae6f-901f62c524a3",
    "name": "Part_12345",
    "file_path": "/programs/part_12345.job"
}
```

#### PlanInfo
```python
{
    "name": "Cutting_Plan_A",
    "material_thickness": 3.0,
    "size_x": 1500.0,
    "size_y": 3000.0,
    "total_parts": 10,
    "estimated_cut_time": 1800.0
}
```

#### RunInfo
```python
{
    "actual_cut_time": 1750.5,
    "actual_stop_time": 45.2,
    "actual_wait_time": 30.1,
    "cut_start_time": "2025-01-15T10:30:00",
    "cut_end_time": "2025-01-15T11:00:00"
}
```

## Configuration

### Machine Configuration

Create a configuration file `machines.json`:

```json
{
    "machines": {
        "Line_1_Machine_A": {
            "url": "opc.tcp://192.168.100.101:56000",
            "description": "Main cutting line - Machine A"
        },
        "Line_1_Machine_B": {
            "url": "opc.tcp://192.168.100.102:56000", 
            "description": "Main cutting line - Machine B"
        }
    },
    "monitoring": {
        "update_interval": 30,
        "retry_attempts": 3,
        "timeout": 10
    }
}
```

### Environment Variables

```bash
# Default OPC UA settings
BYSTRONIC_OPC_TIMEOUT=10
BYSTRONIC_OPC_RETRY_COUNT=3
BYSTRONIC_OPC_LOG_LEVEL=INFO

# Web interface settings
BYSTRONIC_WEB_HOST=0.0.0.0
BYSTRONIC_WEB_PORT=5000
BYSTRONIC_WEB_DEBUG=false
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_connection.py` - Simple connection and data retrieval
- `historical_data.py` - Working with historical data
- `monitoring_dashboard.py` - Multi-machine monitoring
- `data_export.py` - Exporting data to various formats
- `web_interface.py` - Running the web dashboard

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/bystronic-opc.git
cd bystronic-opc
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses Black for code formatting and flake8 for linting:

```bash
black src/
flake8 src/
```

## Requirements

- Python 3.8+
- asyncua >= 1.0.0
- flask >= 2.0.0 (for web interface)
- pillow >= 8.0.0 (for image handling)
- requests >= 2.25.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- Create an issue on GitHub for bugs and feature requests
- Check the documentation in the `docs/` folder
- See examples in the `examples/` directory

## Acknowledgments

- Built on top of the excellent `asyncua` library
- Inspired by industrial automation and Industry 4.0 principles
- Thanks to the open source community for tools and libraries