# Installation Guide

## Requirements

- Python 3.8 or higher
- Access to Bystronic laser cutting machines with OPC UA interface
- Network connectivity to the machines

## Installation Methods

### From PyPI (Recommended)

```bash
pip install bystronic-opc
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/danielristo/bystronic-opc.git
cd bystronic-opc
```

2. Install in development mode:
```bash
pip install -e .
```

### With Optional Dependencies

For web interface support:
```bash
pip install bystronic-opc[web]
```

For development tools:
```bash
pip install bystronic-opc[dev]
```

For documentation building:
```bash
pip install bystronic-opc[docs]
```

All optional dependencies:
```bash
pip install bystronic-opc[web,dev,docs]
```

## Verification

Test your installation:

```python
import bystronic_opc
print(bystronic_opc.__version__)
```

Or run a basic connection test:

```python
import asyncio
from bystronic_opc import BystronicClient

async def test_connection():
    client = BystronicClient("opc.tcp://your-machine-ip:56000")
    try:
        await client.connect()
        print("Connection successful!")
        status = await client.get_machine_status()
        print(f"Machine connected: {status.is_connected}")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await client.disconnect()

# Run the test
asyncio.run(test_connection())
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Check that the machine's OPC UA server is running and accessible
2. **Import errors**: Ensure all dependencies are installed correctly
3. **Async errors**: Make sure you're using `asyncio.run()` or proper async context

### Network Configuration

Ensure your network allows connections to:
- Port 56000 (default OPC UA port for Bystronic machines)
- The machine's IP address is reachable

### Firewall Settings

If you're having connection issues, check that your firewall allows:
- Outgoing connections on port 56000
- TCP connections to the machine network range

## Next Steps

- Check out the [Quick Start Guide](quickstart.md)
- Browse the [examples](../examples/) directory
- Read the [API Reference](api.md)