#!/usr/bin/env python3
"""Multi-machine monitoring example."""

import asyncio
import logging
import json
from datetime import datetime

from bystronic_opc import MachineMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main monitoring example."""
    # Configure multiple machines
    machines = {
        "Machine_1": "opc.tcp://192.168.1.101:56000",
        "Machine_2": "opc.tcp://192.168.1.102:56000", 
        "Machine_3": "opc.tcp://192.168.1.103:56000",
    }
    
    # Create monitor with 30 second update interval
    monitor = MachineMonitor(machines, update_interval=30)
    
    try:
        # Start monitoring
        logger.info("Starting machine monitoring...")
        await monitor.start_monitoring()
        
        # Let it run for a while and periodically check status
        for _ in range(10):  # Run for ~5 minutes (10 * 30 seconds)
            await asyncio.sleep(30)
            
            # Get status of all machines
            all_status = monitor.get_all_machine_status()
            
            print("\\n" + "="*60)
            print(f"Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            for machine_name, status in all_status.items():
                print(f"\\n{machine_name}:")
                print(f"  Connected: {status.is_connected}")
                if status.is_connected:
                    if status.current_job:
                        print(f"  Current Job: {status.current_job.name}")
                    if status.laser_parameters:
                        print(f"  Laser Power: {status.laser_parameters.current_laser_power}")
                        print(f"  Gas Pressure: {status.laser_parameters.gas_pressure}")
                else:
                    if status.error_message:
                        print(f"  Error: {status.error_message}")
                
                if status.last_update:
                    print(f"  Last Update: {status.last_update.strftime('%H:%M:%S')}")
            
            # Show summary
            connected = monitor.get_connected_machines()
            disconnected = monitor.get_disconnected_machines()
            
            print(f"\\nSummary:")
            print(f"  Connected: {len(connected)} machines")
            print(f"  Disconnected: {len(disconnected)} machines")
            
            if connected:
                print(f"  Active: {', '.join(connected)}")
            if disconnected:
                print(f"  Offline: {', '.join(disconnected)}")
    
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
    
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
    
    finally:
        # Stop monitoring
        logger.info("Stopping monitoring...")
        await monitor.stop_monitoring()
        logger.info("Monitoring stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\nExiting...")