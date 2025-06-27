"""
Connection API route tests for the NFC Reader/Writer System PC Server.

This module contains tests for the connection management API endpoints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Test utilities
from server.tests.conftest import async_client, test_db_session
from server.api.app import app
from server.db.models.connection import Connection
from server.db.models.device import Device
from server.db.models.user import User


@pytest.fixture
def test_device(test_db_session: Session) -> Device:
    """Create a test device for testing."""
    device = Device(
        device_id="test-device-001",
        name="Test Android Device",
        model="Test Model X",
        manufacturer="Test Manufacturer",
        android_version="11.0",
        app_version="1.2.3",
        supports_nfc=True,
        supports_ndef=True,
        is_active=True,
        last_connection_type="USB"
    )
    test_db_session.add(device)
    test_db_session.commit()
    test_db_session.refresh(device)
    return device


@pytest.fixture
def test_user(test_db_session: Session) -> User:
    """Create a test user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_admin=False,
        permissions=["read", "write"],
        first_name="Test",
        last_name="User"
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def sample_connection_data(test_device: Device) -> Dict[str, Any]:
    """Sample connection data for testing."""
    return {
        "connection_type": "USB",
        "connected_at": datetime.utcnow().isoformat(),
        "is_active": True,
        "ip_address": "192.168.1.100",
        "port": 8080,
        "usb_serial": "ABC123",
        "device_id": str(test_device.id),
        "user_id": None,
        "connection_info": {"transfer_mode": "MTP"},
        "notes": "Test connection for unit testing"
    }


@pytest.fixture
def sample_connection_with_user_data(test_device: Device, test_user: User) -> Dict[str, Any]:
    """Sample connection data with user for testing."""
    return {
        "connection_type": "Bluetooth",
        "connected_at": datetime.utcnow().isoformat(),
        "is_active": True,
        "ip_address": None,
        "port": None,
        "usb_serial": None,
        "device_id": str(test_device.id),
        "user_id": str(test_user.id),
        "connection_info": {"pairing_code": "1234"},
        "notes": "Test connection with user for unit testing"
    }


class TestConnectionCRUD:
    """Test cases for Connection CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_connection_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful connection creation (happy path)."""
        response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["connection_type"] == sample_connection_data["connection_type"]
        assert data["is_active"] == sample_connection_data["is_active"]
        assert data["ip_address"] == sample_connection_data["ip_address"]
        assert int(data["port"]) == sample_connection_data["port"] if data["port"] else None
        assert data["usb_serial"] == sample_connection_data["usb_serial"]
        assert data["device_id"] == sample_connection_data["device_id"]
        assert data["user_id"] == sample_connection_data["user_id"]
        assert data["connection_info"] == sample_connection_data["connection_info"]
        assert data["notes"] == sample_connection_data["notes"]
        
        # Verify database entry
        connection_id = uuid.UUID(data["id"])
        db_connection = test_db_session.query(Connection).filter(Connection.id == connection_id).first()
        assert db_connection is not None
        assert db_connection.connection_type == sample_connection_data["connection_type"]
        assert db_connection.is_active == sample_connection_data["is_active"]
        
        # Verify device's last connection type was updated
        device_id = uuid.UUID(sample_connection_data["device_id"])
        device = test_db_session.query(Device).filter(Device.id == device_id).first()
        assert device.last_connection_type == sample_connection_data["connection_type"]

    @pytest.mark.asyncio
    async def test_create_connection_with_user_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_with_user_data: Dict[str, Any]
    ):
        """Test successful connection creation with user (happy path)."""
        response = await async_client.post("/api/v1/connections/", json=sample_connection_with_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["connection_type"] == sample_connection_with_user_data["connection_type"]
        assert data["user_id"] == sample_connection_with_user_data["user_id"]
        
        # Verify database entry
        connection_id = uuid.UUID(data["id"])
        db_connection = test_db_session.query(Connection).filter(Connection.id == connection_id).first()
        assert db_connection is not None
        assert db_connection.user_id == uuid.UUID(sample_connection_with_user_data["user_id"])

    @pytest.mark.asyncio
    async def test_create_connection_nonexistent_device(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test connection creation with non-existent device returns 404."""
        # Modify device_id to non-existent one
        sample_connection_data["device_id"] = str(uuid.uuid4())
        
        response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
        assert "device" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_connection_nonexistent_user(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test connection creation with non-existent user returns 404."""
        # Add non-existent user_id
        sample_connection_data["user_id"] = str(uuid.uuid4())
        
        response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
        assert "user" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_connections_list_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any],
        sample_connection_with_user_data: Dict[str, Any]
    ):
        """Test successful retrieval of connections list with pagination and filtering."""
        # Create multiple connections
        await async_client.post("/api/v1/connections/", json=sample_connection_data)
        await async_client.post("/api/v1/connections/", json=sample_connection_with_user_data)
        
        # Retrieve all connections
        response = await async_client.get("/api/v1/connections/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Test pagination
        response_paginated = await async_client.get("/api/v1/connections/?skip=0&limit=1")
        assert response_paginated.status_code == 200
        paginated_data = response_paginated.json()
        assert len(paginated_data) == 1
        
        # Test filtering by active status
        response_active = await async_client.get("/api/v1/connections/?is_active=true")
        assert response_active.status_code == 200
        active_data = response_active.json()
        assert all(conn["is_active"] for conn in active_data)
        
        # Test filtering by connection type
        response_conn_type = await async_client.get("/api/v1/connections/?connection_type=USB")
        assert response_conn_type.status_code == 200
        conn_type_data = response_conn_type.json()
        assert all(conn["connection_type"] == "USB" for conn in conn_type_data)
        
        # Test filtering by device ID
        device_id = sample_connection_data["device_id"]
        response_device = await async_client.get(f"/api/v1/connections/?device_id={device_id}")
        assert response_device.status_code == 200
        device_data = response_device.json()
        assert all(conn["device_id"] == device_id for conn in device_data)
        
        # Test filtering by user ID
        user_id = sample_connection_with_user_data["user_id"]
        response_user = await async_client.get(f"/api/v1/connections/?user_id={user_id}")
        assert response_user.status_code == 200
        user_data = response_user.json()
        assert all(conn["user_id"] == user_id for conn in user_data)

    @pytest.mark.asyncio
    async def test_get_connection_by_id_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful retrieval of a connection by ID."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Retrieve connection
        response = await async_client.get(f"/api/v1/connections/{connection_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == connection_id
        assert data["connection_type"] == sample_connection_data["connection_type"]
        assert data["device_id"] == sample_connection_data["device_id"]

    @pytest.mark.asyncio
    async def test_get_connection_by_id_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent connection returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/connections/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_device_connections_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        test_device: Device,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful retrieval of connections for a specific device."""
        # Create connection first
        await async_client.post("/api/v1/connections/", json=sample_connection_data)
        
        # Create another connection for same device but different type
        another_connection = sample_connection_data.copy()
        another_connection["connection_type"] = "WiFi"
        another_connection["ip_address"] = "192.168.1.101"
        another_connection["port"] = 8081
        another_connection["usb_serial"] = None
        await async_client.post("/api/v1/connections/", json=another_connection)
        
        # Retrieve connections for device
        device_id = str(test_device.id)
        response = await async_client.get(f"/api/v1/connections/device/{device_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert all(conn["device_id"] == device_id for conn in data)
        
        # Test with filtering
        response_filtered = await async_client.get(f"/api/v1/connections/device/{device_id}?is_active=true")
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        assert all(conn["is_active"] for conn in filtered_data)

    @pytest.mark.asyncio
    async def test_get_device_connections_nonexistent_device(
        self,
        async_client: AsyncClient
    ):
        """Test retrieving connections for non-existent device returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/connections/device/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
        assert "device" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_connection_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        test_user: User,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful connection update."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Update connection
        update_data = {
            "notes": "Updated connection notes",
            "connection_info": {"transfer_mode": "PTP", "speed": "high"},
            "user_id": str(test_user.id)
        }
        
        response = await async_client.put(f"/api/v1/connections/{connection_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == connection_id
        assert data["notes"] == update_data["notes"]
        assert data["connection_info"] == update_data["connection_info"]
        assert data["user_id"] == update_data["user_id"]
        
        # Verify connection_type remained unchanged
        assert data["connection_type"] == sample_connection_data["connection_type"]

    @pytest.mark.asyncio
    async def test_update_connection_nonexistent_user(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test connection update with non-existent user returns 404."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Update with non-existent user
        update_data = {
            "user_id": str(uuid.uuid4())
        }
        
        response = await async_client.put(f"/api/v1/connections/{connection_id}", json=update_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
        assert "user" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_close_connection_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful connection closure."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Close connection
        close_data = {
            "disconnected_at": datetime.utcnow().isoformat(),
            "notes": "Connection closed normally"
        }
        
        response = await async_client.patch(f"/api/v1/connections/{connection_id}/close", json=close_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == connection_id
        assert data["is_active"] is False
        assert data["disconnected_at"] is not None
        assert data["notes"] == close_data["notes"]

    @pytest.mark.asyncio
    async def test_close_connection_already_closed(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test closing an already closed connection returns 400."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Close connection
        close_data = {
            "disconnected_at": datetime.utcnow().isoformat()
        }
        
        response1 = await async_client.patch(f"/api/v1/connections/{connection_id}/close", json=close_data)
        assert response1.status_code == 200
        
        # Try to close again
        response2 = await async_client.patch(f"/api/v1/connections/{connection_id}/close", json=close_data)
        assert response2.status_code == 400
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already closed" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_connection_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any]
    ):
        """Test successful connection deletion."""
        # Create connection first
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        # Delete connection
        response = await async_client.delete(f"/api/v1/connections/{connection_id}")
        assert response.status_code == 204
        
        # Verify connection is deleted
        get_response = await async_client.get(f"/api/v1/connections/{connection_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_active_connections(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_connection_data: Dict[str, Any],
        sample_connection_with_user_data: Dict[str, Any]
    ):
        """Test retrieval of active connections."""
        # Create active connections
        await async_client.post("/api/v1/connections/", json=sample_connection_data)
        await async_client.post("/api/v1/connections/", json=sample_connection_with_user_data)
        
        # Create and close a connection
        create_response = await async_client.post("/api/v1/connections/", json=sample_connection_data)
        assert create_response.status_code == 201
        connection_id = create_response.json()["id"]
        
        close_response = await async_client.patch(f"/api/v1/connections/{connection_id}/close")
        assert close_response.status_code == 200
        
        # Get active connections
        response = await async_client.get("/api/v1/connections/active/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        assert all(conn["is_active"] for conn in data)
        
        # Test filtering by connection type
        response_filtered = await async_client.get("/api/v1/connections/active/?connection_type=USB")
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        assert all(conn["is_active"] for conn in filtered_data)
        assert all(conn["connection_type"] == "USB" for conn in filtered_data)
        # Check if any connection has the matching usb_serial, handling null values
        if filtered_data and "usb_serial" in filtered_data[0]:
            assert any(conn.get("usb_serial") == sample_connection_data["usb_serial"] for conn in filtered_data)
