"""Main Bystronic OPC UA Client implementation."""

import asyncio
import struct
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import io

from asyncua import Client, ua
from PIL import Image

from .data_types import (
    JobInfo, 
    PlanInfo, 
    PartInfo, 
    RunInfo, 
    LaserParameters,
    MachineStatus,
    HistoryQuery
)
from .exceptions import ConnectionError, DataError, MethodCallError


class BystronicClient:
    """Client for connecting to Bystronic laser cutting machines via OPC UA."""
    
    # OPC UA method definitions
    METHODS = {
        "GetJobInfo": "History.GetJobInfo",
        "GetPlanInfos": "History.GetPlanInfos", 
        "GetPartInfos": "History.GetPartInfos",
        "GetRunInfo": "History.GetRunInfo",
        "GetRunStatesHistory": "History.GetRunStatesHistory",
        "GetScreenImage": "ImageProvider.GetScreenImage",
        "GetRunHistory": "History.GetRunHistory",
        "GetRunPartHistory": "History.GetRunPartHistory",
        "GetMachineStateHistory": "History.GetMachineStateHistory",
        "GetMessageHistory": "History.GetMessageHistory",
        "GetPlateOperatingDataHistory": "History.GetPlateOperatingDataHistory",
        "GetPartOperatingDataHistory": "History.GetPartOperatingDataHistory",
    }
    
    # Laser parameter node IDs
    LASER_NODES = [
        "ns=2;s=Laser.CurrentLaserPower",
        "ns=2;s=Laser.GasChannel", 
        "ns=2;s=Laser.GasPressure",
        "ns=2;s=Laser.LaserPowerDeviation",
        "ns=2;s=Laser.LaserPowerSetpoint",
        "ns=2;s=Laser.ProcessOperationMode",
    ]
    
    def __init__(self, url: str, timeout: int = 10):
        """Initialize the Bystronic OPC UA client.
        
        Args:
            url: OPC UA server URL (e.g., "opc.tcp://192.168.1.100:56000")
            timeout: Connection timeout in seconds
        """
        self.url = url
        self.timeout = timeout
        self._client = Client(url)
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to the OPC UA server."""
        try:
            await self._client.connect()
            self._connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to {self.url}: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the OPC UA server."""
        if self._connected:
            await self._client.disconnect()
            self._connected = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if not self._connected:
            raise ConnectionError("Client is not connected. Call connect() first.")
    
    async def _call_method(
        self,
        object_node_id: str,
        method_node_id: str,
        input_args: List[ua.Variant]
    ) -> Any:
        """Call an OPC UA method with error handling.
        
        Args:
            object_node_id: Object node identifier
            method_node_id: Method node identifier  
            input_args: List of input arguments
            
        Returns:
            Method result
        """
        self._ensure_connected()
        
        try:
            object_node = self._client.get_node(object_node_id)
            method_node = self._client.get_node(method_node_id)
            result = await object_node.call_method(method_node, *input_args)
            return result
        except Exception as e:
            raise MethodCallError(f"Method call failed {method_node_id}: {e}")
    
    def _decode_job_info(self, extension_object) -> Optional[JobInfo]:
        """Decode job information from OPC UA extension object."""
        if extension_object is None:
            return None
        
        try:
            body = extension_object.Body
            if len(body) < 36:
                return None
            
            # Extract GUID
            guid_parts = struct.unpack("<IHH8s", body[:16])
            guid_str = f"{guid_parts[0]:08x}-{guid_parts[1]:04x}-{guid_parts[2]:04x}-{guid_parts[3].hex()[:4]}-{guid_parts[3].hex()[4:]}"
            
            # Extract name
            name_length = struct.unpack("<I", body[32:36])[0]
            name = body[36:36 + name_length].decode("utf-8")
            
            # Extract file path
            file_path_start = 36 + name_length
            file_path_length = struct.unpack("<I", body[file_path_start:file_path_start + 4])[0]
            file_path = body[file_path_start + 4:file_path_start + 4 + file_path_length].decode("utf-8")
            
            return JobInfo(
                guid=UUID(guid_str),
                name=name,
                file_path=file_path
            )
        except Exception as e:
            raise DataError(f"Failed to decode job info: {e}")
    
    def _decode_plan_info(self, extension_object) -> Optional[PlanInfo]:
        """Decode plan information from OPC UA extension object."""
        if extension_object is None:
            return None
        
        try:
            body = extension_object.Body
            if len(body) < 36:
                return None
            
            # Extract job GUID
            job_guid_parts = struct.unpack("<IHH8s", body[:16])
            job_guid_str = f"{job_guid_parts[0]:08x}-{job_guid_parts[1]:04x}-{job_guid_parts[2]:04x}-{job_guid_parts[3].hex()[:4]}-{job_guid_parts[3].hex()[4:]}"
            
            # Extract plan GUID
            plan_guid_parts = struct.unpack("<IHH8s", body[16:32])
            plan_guid_str = f"{plan_guid_parts[0]:08x}-{plan_guid_parts[1]:04x}-{plan_guid_parts[2]:04x}-{plan_guid_parts[3].hex()[:4]}-{plan_guid_parts[3].hex()[4:]}"
            
            # Extract name
            name_length = struct.unpack("<I", body[32:36])[0]
            name = body[36:36 + name_length].decode("utf-8")
            
            # Extract additional plan information
            offset = 36 + name_length
            size_x, size_y, material_thickness = struct.unpack("<ddd", body[offset:offset + 24])
            offset += 24
            
            total_runs, total_parts = struct.unpack("<ii", body[offset:offset + 8])
            offset += 8
            
            plan_state = struct.unpack("<i", body[offset:offset + 4])[0]
            offset += 4
            
            estimated_cut_time = struct.unpack("<d", body[offset:offset + 8])[0]
            
            return PlanInfo(
                job_guid=UUID(job_guid_str),
                plan_guid=UUID(plan_guid_str),
                name=name,
                size_x=size_x,
                size_y=size_y,
                material_thickness=material_thickness,
                total_runs=total_runs,
                total_parts=total_parts,
                plan_state=plan_state,
                estimated_cut_time=estimated_cut_time
            )
        except Exception as e:
            raise DataError(f"Failed to decode plan info: {e}")
    
    async def get_current_job(self) -> Optional[JobInfo]:
        """Get current job information from the machine.
        
        Returns:
            Current job information or None if no job is active
        """
        try:
            work_node = await self._client.nodes.root.get_child(["0:Objects", "2:Work"])
            current_job = await (await work_node.get_child(["2:CurrentJob"])).get_value()
            return self._decode_job_info(current_job)
        except Exception as e:
            raise DataError(f"Failed to get current job: {e}")
    
    async def get_job_info(self, job_guid: UUID) -> Optional[Dict[str, Any]]:
        """Get detailed job information by GUID.
        
        Args:
            job_guid: Job GUID to query
            
        Returns:
            Job information dictionary
        """
        input_args = [ua.Variant(job_guid, ua.VariantType.Guid)]
        result = await self._call_method(
            ua.NodeId("History", 2),
            ua.NodeId("History.GetJobInfo", 2),
            input_args
        )
        return json.loads(result) if result else None
    
    async def get_plan_info(self, job_guid: UUID) -> Optional[Dict[str, Any]]:
        """Get plan information for a job.
        
        Args:
            job_guid: Job GUID to query
            
        Returns:
            Plan information dictionary
        """
        input_args = [ua.Variant(job_guid, ua.VariantType.Guid)]
        result = await self._call_method(
            ua.NodeId("History", 2),
            ua.NodeId("History.GetPlanInfos", 2),
            input_args
        )
        if result:
            data = json.loads(result)
            return data[0] if data else None
        return None
    
    async def get_part_info(self, job_guid: UUID) -> Optional[Dict[str, Any]]:
        """Get part information for a job.
        
        Args:
            job_guid: Job GUID to query
            
        Returns:
            Part information dictionary
        """
        input_args = [ua.Variant(job_guid, ua.VariantType.Guid)]
        result = await self._call_method(
            ua.NodeId("History", 2),
            ua.NodeId("History.GetPartInfos", 2),
            input_args
        )
        if result and result != "[]":
            data = json.loads(result)
            return data[0] if data else None
        return None
    
    async def get_run_history(
        self, 
        from_timestamp: datetime, 
        to_timestamp: datetime,
        page: int = 1,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """Get run history within a time range.
        
        Args:
            from_timestamp: Start time
            to_timestamp: End time
            page: Page number (default: 1)
            page_size: Number of entries per page (default: 100)
            
        Returns:
            List of run history entries
        """
        input_args = [
            ua.Variant(from_timestamp, ua.VariantType.DateTime),
            ua.Variant(to_timestamp, ua.VariantType.DateTime),
            ua.Variant(page, ua.VariantType.Int32),
            ua.Variant(page_size, ua.VariantType.Int32),
        ]
        
        result = await self._call_method(
            ua.NodeId("History", 2),
            ua.NodeId("History.GetRunHistory", 2),
            input_args
        )
        
        if result and len(result) > 1:
            return json.loads(result[1])
        return []
    
    async def get_laser_parameters(self) -> LaserParameters:
        """Get current laser parameters.
        
        Returns:
            Current laser parameters
        """
        values = {}
        
        for node_id in self.LASER_NODES:
            try:
                node = self._client.get_node(node_id)
                value = await node.read_value()
                values[node_id.split('.')[-1]] = value
            except Exception as e:
                print(f"Failed to read {node_id}: {e}")
                values[node_id.split('.')[-1]] = None
        
        return LaserParameters(
            current_laser_power=values.get('CurrentLaserPower', 0.0),
            gas_channel=values.get('GasChannel', 0),
            gas_pressure=values.get('GasPressure', 0.0),
            laser_power_deviation=values.get('LaserPowerDeviation', 0.0),
            laser_power_setpoint=values.get('LaserPowerSetpoint', 0.0),
            process_operation_mode=values.get('ProcessOperationMode', 0)
        )
    
    async def get_screen_image(self) -> bytes:
        """Capture machine screen image.
        
        Returns:
            PNG image data as bytes
        """
        input_args = [
            ua.Variant(1200, ua.VariantType.Int32),  # page
            ua.Variant(0, ua.VariantType.Int32),     # page size
        ]
        
        result = await self._call_method(
            ua.NodeId("ImageProvider", 2),
            ua.NodeId("ImageProvider.GetScreenImage", 2),
            input_args
        )
        
        return result
    
    async def get_machine_status(self) -> MachineStatus:
        """Get comprehensive machine status.
        
        Returns:
            Current machine status
        """
        try:
            current_job = await self.get_current_job()
            laser_params = await self.get_laser_parameters()
            
            return MachineStatus(
                machine_url=self.url,
                is_connected=self._connected,
                current_job=current_job,
                laser_parameters=laser_params,
                last_update=datetime.now()
            )
        except Exception as e:
            return MachineStatus(
                machine_url=self.url,
                is_connected=False,
                error_message=str(e),
                last_update=datetime.now()
            )