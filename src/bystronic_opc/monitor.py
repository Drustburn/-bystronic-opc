"""Multi-machine monitoring implementation."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .client import BystronicClient
from .data_types import MachineStatus
from .exceptions import ConnectionError


logger = logging.getLogger(__name__)


class MachineMonitor:
    """Monitor multiple Bystronic machines simultaneously."""
    
    def __init__(
        self,
        machines: Dict[str, str],
        update_interval: int = 30,
        retry_attempts: int = 3
    ):
        """Initialize machine monitor.
        
        Args:
            machines: Dictionary of machine name -> OPC UA URL
            update_interval: Update interval in seconds
            retry_attempts: Number of retry attempts for failed connections
        """
        self.machines = machines
        self.update_interval = update_interval
        self.retry_attempts = retry_attempts
        self._clients: Dict[str, BystronicClient] = {}
        self._status: Dict[str, MachineStatus] = {}
        self._monitoring = False
        self._tasks: List[asyncio.Task] = []
        
        # Initialize clients
        for name, url in machines.items():
            self._clients[name] = BystronicClient(url)
            self._status[name] = MachineStatus(
                machine_url=url,
                is_connected=False
            )
    
    async def start_monitoring(self) -> None:
        """Start monitoring all machines."""
        if self._monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self._monitoring = True
        logger.info(f"Starting monitoring for {len(self.machines)} machines")
        
        # Create monitoring tasks for each machine
        for machine_name in self.machines:
            task = asyncio.create_task(self._monitor_machine(machine_name))
            self._tasks.append(task)
        
        logger.info("Machine monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring all machines."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        logger.info("Stopping machine monitoring")
        
        # Cancel all monitoring tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
        # Disconnect all clients
        for client in self._clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")
        
        logger.info("Machine monitoring stopped")
    
    async def _monitor_machine(self, machine_name: str) -> None:
        """Monitor a single machine continuously.
        
        Args:
            machine_name: Name of the machine to monitor
        """
        client = self._clients[machine_name]
        retry_count = 0
        
        while self._monitoring:
            try:
                # Ensure connection
                if not client._connected:
                    await client.connect()
                    retry_count = 0
                    logger.info(f"Connected to {machine_name}")
                
                # Get machine status
                status = await client.get_machine_status()
                self._status[machine_name] = status
                
                logger.debug(f"Updated status for {machine_name}")
                
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
            except ConnectionError as e:
                retry_count += 1
                logger.error(f"Connection error for {machine_name}: {e}")
                
                if retry_count <= self.retry_attempts:
                    wait_time = min(retry_count * 10, 60)  # Exponential backoff
                    logger.info(f"Retrying {machine_name} in {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries reached for {machine_name}")
                    self._status[machine_name] = MachineStatus(
                        machine_url=client.url,
                        is_connected=False,
                        error_message=str(e),
                        last_update=datetime.now()
                    )
                    await asyncio.sleep(self.update_interval)
                    retry_count = 0  # Reset for next attempt
            
            except Exception as e:
                logger.error(f"Unexpected error monitoring {machine_name}: {e}")
                self._status[machine_name] = MachineStatus(
                    machine_url=client.url,
                    is_connected=False,
                    error_message=str(e),
                    last_update=datetime.now()
                )
                await asyncio.sleep(self.update_interval)
    
    def get_machine_status(self, machine_name: str) -> Optional[MachineStatus]:
        """Get status of a specific machine.
        
        Args:
            machine_name: Name of the machine
            
        Returns:
            Machine status or None if not found
        """
        return self._status.get(machine_name)
    
    def get_all_machine_status(self) -> Dict[str, MachineStatus]:
        """Get status of all machines.
        
        Returns:
            Dictionary of machine name -> status
        """
        return self._status.copy()
    
    def get_connected_machines(self) -> List[str]:
        """Get list of currently connected machines.
        
        Returns:
            List of connected machine names
        """
        return [
            name for name, status in self._status.items()
            if status.is_connected
        ]
    
    def get_disconnected_machines(self) -> List[str]:
        """Get list of currently disconnected machines.
        
        Returns:
            List of disconnected machine names
        """
        return [
            name for name, status in self._status.items()
            if not status.is_connected
        ]
    
    async def get_machine_client(self, machine_name: str) -> Optional[BystronicClient]:
        """Get client for a specific machine.
        
        Args:
            machine_name: Name of the machine
            
        Returns:
            Client instance or None if not found
        """
        return self._clients.get(machine_name)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()