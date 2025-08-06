#!/usr/bin/env python3
"""Basic connection example for Bystronic OPC UA client."""

import asyncio
import logging
from datetime import datetime, timedelta

from bystronic_opc import BystronicClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main example function."""
    # Machine configuration
    machine_url = "opc.tcp://192.168.1.100:56000"  # Replace with your machine IP
    
    # Create client
    client = BystronicClient(machine_url)
    
    try:
        # Connect to machine
        logger.info(f"Connecting to {machine_url}...")
        await client.connect()
        logger.info("Connected successfully!")
        
        # Get current job information
        logger.info("Getting current job information...")
        current_job = await client.get_current_job()
        if current_job:
            logger.info(f"Current Job: {current_job.name} (GUID: {current_job.guid})")
            logger.info(f"File Path: {current_job.file_path}")
        else:
            logger.info("No job currently active")
        
        # Get laser parameters
        logger.info("Getting laser parameters...")
        laser_params = await client.get_laser_parameters()
        logger.info(f"Laser Power: {laser_params.current_laser_power}")
        logger.info(f"Gas Pressure: {laser_params.gas_pressure}")
        logger.info(f"Operation Mode: {laser_params.process_operation_mode}")
        
        # Get historical run data (last 24 hours)
        logger.info("Getting run history...")
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        run_history = await client.get_run_history(start_time, end_time)
        logger.info(f"Found {len(run_history)} runs in the last 24 hours")
        
        for i, run in enumerate(run_history[:5]):  # Show first 5 runs
            logger.info(f"Run {i+1}: Job GUID {run.get('JobGuid')}, "
                       f"Start: {run.get('CutStartTime')}")
        
        # Get machine status summary
        logger.info("Getting machine status...")
        status = await client.get_machine_status()
        logger.info(f"Machine Status: Connected={status.is_connected}")
        if status.current_job:
            logger.info(f"Current Job: {status.current_job.name}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    
    finally:
        # Always disconnect
        await client.disconnect()
        logger.info("Disconnected from machine")


if __name__ == "__main__":
    asyncio.run(main())