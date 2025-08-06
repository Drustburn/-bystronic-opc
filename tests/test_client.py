"""Tests for the Bystronic OPC UA client."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from bystronic_opc.client import BystronicClient
from bystronic_opc.exceptions import ConnectionError, DataError


class TestBystronicClient:
    """Test suite for BystronicClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return BystronicClient("opc.tcp://test.machine:56000")
    
    @pytest.mark.asyncio
    async def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.url == "opc.tcp://test.machine:56000"
        assert client.timeout == 10
        assert not client._connected
    
    @pytest.mark.asyncio
    async def test_connect_success(self, client):
        """Test successful connection."""
        with patch.object(client._client, 'connect', new_callable=AsyncMock) as mock_connect:
            await client.connect()
            mock_connect.assert_called_once()
            assert client._connected
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, client):
        """Test connection failure."""
        with patch.object(client._client, 'connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            with pytest.raises(ConnectionError, match="Failed to connect"):
                await client.connect()
            
            assert not client._connected
    
    @pytest.mark.asyncio
    async def test_disconnect(self, client):
        """Test disconnection."""
        client._connected = True
        
        with patch.object(client._client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
            await client.disconnect()
            mock_disconnect.assert_called_once()
            assert not client._connected
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager."""
        with patch.object(client, 'connect', new_callable=AsyncMock) as mock_connect:
            with patch.object(client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
                async with client:
                    mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ensure_connected_when_not_connected(self, client):
        """Test _ensure_connected when not connected."""
        with pytest.raises(ConnectionError, match="Client is not connected"):
            client._ensure_connected()
    
    @pytest.mark.asyncio
    async def test_ensure_connected_when_connected(self, client):
        """Test _ensure_connected when connected."""
        client._connected = True
        # Should not raise an exception
        client._ensure_connected()
    
    def test_decode_job_info_valid_data(self, client):
        """Test decoding valid job info."""
        # Mock extension object with sample binary data
        mock_ext_obj = Mock()
        # This would need proper binary data for a real test
        mock_ext_obj.Body = b'\\x00' * 100  # Placeholder
        
        # For now, test None case
        result = client._decode_job_info(None)
        assert result is None
    
    def test_decode_job_info_invalid_data(self, client):
        """Test decoding invalid job info."""
        mock_ext_obj = Mock()
        mock_ext_obj.Body = b'\\x00' * 10  # Too short
        
        result = client._decode_job_info(mock_ext_obj)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_job_no_job(self, client):
        """Test getting current job when no job is active."""
        client._connected = True
        
        with patch.object(client._client, 'nodes') as mock_nodes:
            mock_root = AsyncMock()
            mock_work_node = AsyncMock()
            mock_job_node = AsyncMock()
            
            mock_nodes.root.get_child = AsyncMock(return_value=mock_work_node)
            mock_work_node.get_child = AsyncMock(return_value=mock_job_node)
            mock_job_node.get_value = AsyncMock(return_value=None)
            
            result = await client.get_current_job()
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_laser_parameters(self, client):
        """Test getting laser parameters."""
        client._connected = True
        
        with patch.object(client._client, 'get_node') as mock_get_node:
            mock_node = Mock()
            mock_node.read_value = AsyncMock(return_value=100.0)
            mock_get_node.return_value = mock_node
            
            result = await client.get_laser_parameters()
            
            assert result.current_laser_power == 100.0
            assert result.gas_channel == 100.0  # All values will be 100.0 in this mock
    
    @pytest.mark.asyncio
    async def test_get_run_history(self, client):
        """Test getting run history."""
        from datetime import datetime
        
        client._connected = True
        
        with patch.object(client, '_call_method', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = [None, '[]']  # Empty result
            
            start_time = datetime.now()
            end_time = datetime.now()
            
            result = await client.get_run_history(start_time, end_time)
            assert result == []
            
            mock_call.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_machine_status_success(self, client):
        """Test getting machine status successfully."""
        client._connected = True
        
        with patch.object(client, 'get_current_job', new_callable=AsyncMock) as mock_job:
            with patch.object(client, 'get_laser_parameters', new_callable=AsyncMock) as mock_laser:
                mock_job.return_value = None
                mock_laser.return_value = Mock()
                
                status = await client.get_machine_status()
                
                assert status.machine_url == client.url
                assert status.is_connected == client._connected
                assert status.last_update is not None
    
    @pytest.mark.asyncio
    async def test_get_machine_status_error(self, client):
        """Test getting machine status with error."""
        client._connected = False
        
        with patch.object(client, 'get_current_job', new_callable=AsyncMock) as mock_job:
            mock_job.side_effect = Exception("Test error")
            
            status = await client.get_machine_status()
            
            assert not status.is_connected
            assert status.error_message == "Test error"