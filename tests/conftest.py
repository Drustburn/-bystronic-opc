"""Test configuration and fixtures."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from bystronic_opc.data_types import JobInfo, PlanInfo, PartInfo, MachineStatus


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_opc_client():
    """Mock OPC UA client for testing."""
    client = Mock()
    client.connect = AsyncMock()
    client.disconnect = AsyncMock()
    client.get_node = Mock()
    return client


@pytest.fixture
def sample_job_info():
    """Sample job information for testing."""
    return JobInfo(
        guid=uuid4(),
        name="Test Job",
        file_path="/programs/test_job.job"
    )


@pytest.fixture
def sample_plan_info():
    """Sample plan information for testing."""
    return PlanInfo(
        job_guid=uuid4(),
        plan_guid=uuid4(),
        name="Test Plan",
        size_x=1500.0,
        size_y=3000.0,
        material_thickness=3.0,
        total_runs=5,
        total_parts=50,
        plan_state=1,
        estimated_cut_time=1800.0
    )


@pytest.fixture
def sample_machine_status():
    """Sample machine status for testing."""
    return MachineStatus(
        machine_url="opc.tcp://test.machine:56000",
        is_connected=True
    )


@pytest.fixture
def machine_config():
    """Sample machine configuration for testing."""
    return {
        "Test_Machine_1": "opc.tcp://192.168.1.101:56000",
        "Test_Machine_2": "opc.tcp://192.168.1.102:56000"
    }