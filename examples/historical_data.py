#!/usr/bin/env python3
"""Historical data retrieval example."""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from uuid import UUID

from bystronic_opc import BystronicClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main historical data example."""
    # Machine configuration
    machine_url = "opc.tcp://192.168.1.100:56000"  # Replace with your machine IP
    
    async with BystronicClient(machine_url) as client:
        logger.info(f"Connected to {machine_url}")
        
        # Define time range (last 7 days)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        logger.info(f"Retrieving data from {start_time} to {end_time}")
        
        # Get run history
        logger.info("Getting run history...")
        runs = await client.get_run_history(start_time, end_time, page_size=50)
        logger.info(f"Found {len(runs)} runs")
        
        # Analyze the data
        total_jobs = set()
        total_cut_time = 0
        
        for run in runs:
            job_guid = run.get('JobGuid')
            run_guid = run.get('RunGuid')
            
            if job_guid:
                total_jobs.add(job_guid)
            
            # Get detailed information for each run
            logger.info(f"\\nProcessing run: {run_guid}")
            logger.info(f"  Job GUID: {job_guid}")
            logger.info(f"  Start Time: {run.get('CutStartTime')}")
            logger.info(f"  End Time: {run.get('CutEndTime')}")
            
            # Get job information
            if job_guid:
                try:
                    job_info = await client.get_job_info(UUID(job_guid))
                    if job_info:
                        logger.info(f"  Job Name: {job_info.get('Name', 'Unknown')}")
                    
                    # Get plan information
                    plan_info = await client.get_plan_info(UUID(job_guid))
                    if plan_info:
                        logger.info(f"  Plan: {plan_info.get('Name', 'Unknown')}")
                        logger.info(f"  Material: {plan_info.get('MaterialThickness', 0)}mm")
                    
                    # Get part information
                    part_info = await client.get_part_info(UUID(job_guid))
                    if part_info:
                        logger.info(f"  Part: {part_info.get('Name', 'Unknown')}")
                        logger.info(f"  Quantity: {part_info.get('Quantity', 0)}")
                        logger.info(f"  Order: {part_info.get('OrderInfo', 'N/A')}")
                
                except Exception as e:
                    logger.error(f"  Error getting job details: {e}")
            
            # Add small delay to avoid overwhelming the server
            await asyncio.sleep(0.5)
        
        # Summary
        logger.info("\\n" + "="*50)
        logger.info("SUMMARY")
        logger.info("="*50)
        logger.info(f"Time Period: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
        logger.info(f"Total Runs: {len(runs)}")
        logger.info(f"Unique Jobs: {len(total_jobs)}")
        
        # Calculate production statistics
        if runs:
            runs_with_times = [r for r in runs if r.get('CutStartTime') and r.get('CutEndTime')]
            if runs_with_times:
                logger.info(f"Runs with timing data: {len(runs_with_times)}")
                
                # Calculate average run time (if possible)
                # Note: This would require parsing the timestamp strings
                logger.info("Timing analysis would require date parsing implementation")


async def analyze_machine_utilization(client: BystronicClient, days: int = 7):
    """Analyze machine utilization over a time period."""
    logger.info(f"Analyzing machine utilization for last {days} days")
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Get machine state history
    # Note: This would require implementing the machine state history method
    logger.info("Machine state analysis not yet implemented")
    
    # For now, just analyze run frequency
    runs = await client.get_run_history(start_time, end_time, page_size=1000)
    
    if runs:
        # Group by day
        daily_runs = {}
        for run in runs:
            start_time_str = run.get('CutStartTime')
            if start_time_str:
                try:
                    # Parse the date (simplified)
                    date = start_time_str.split('T')[0]
                    daily_runs[date] = daily_runs.get(date, 0) + 1
                except Exception:
                    continue
        
        logger.info("\\nDaily run counts:")
        for date, count in sorted(daily_runs.items()):
            logger.info(f"  {date}: {count} runs")


if __name__ == "__main__":
    asyncio.run(main())