"""
Device API route tests for the NFC Reader/Writer System PC Server.

This module contains tests for the device management API endpoints.
"""

import uuid
from typing import Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Test utilities
from server.tests.conftest import async_client, test_db_session
from server.api.app import app
from server.db.models.device import Device


@pytest.fixture
def sample_device_data() -> Dict[str, Any]:
    """Sample device data for testing."""
    return {
        "device_id": "test-device-001",
        "name": "Test Android Device",
        "model": "Test Model X",
        "manufacturer": "Test Manufacturer",
        "android_version": "11.0",
        "app_version": "1.2.3",
        "supports_nfc": True,
        "supports_ndef": True,
        "is_active": True,
        "last_connection_type": "USB",
        "device_info": {"cpu": "octa-core", "ram": "8GB"},
        "notes": "Test device for unit testing"
    }


@pytest.fixture
def inactive_device_data() -> Dict[str, Any]:
    """Sample inactive device data for testing."""
    return {
        "device_id": "test-device-002",
        "name": "Inactive Test Device",
        "model": "Test Model Y",
        "manufacturer": "Test Manufacturer",
        "android_version": "10.0",
        "app_version": "1.2.0",
        "supports_nfc": True,
        "supports_ndef": False,
        "is_active": False,
        "last_connection_type": "Bluetooth",
        "device_info": {"cpu": "quad-core", "ram": "4GB"},
        "notes": "Inactive test device for unit testing"
    }


class TestDeviceCRUD:
    """Test cases for Device CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_device_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test successful device creation (happy path)."""
        response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["device_id"] == sample_device_data["device_id"]
        assert data["name"] == sample_device_data["name"]
        assert data["model"] == sample_device_data["model"]
        assert data["manufacturer"] == sample_device_data["manufacturer"]
        assert data["android_version"] == sample_device_data["android_version"]
        assert data["app_version"] == sample_device_data["app_version"]
        assert data["supports_nfc"] == sample_device_data["supports_nfc"]
        assert data["supports_ndef"] == sample_device_data["supports_ndef"]
        assert data["is_active"] == sample_device_data["is_active"]
        assert data["last_connection_type"] == sample_device_data["last_connection_type"]
        assert data["device_info"] == sample_device_data["device_info"]
        assert data["notes"] == sample_device_data["notes"]
        
        # Verify database entry
        device_id = uuid.UUID(data["id"])
        db_device = test_db_session.query(Device).filter(Device.id == device_id).first()
        assert db_device is not None
        assert db_device.device_id == sample_device_data["device_id"]
        assert db_device.name == sample_device_data["name"]

    @pytest.mark.asyncio
    async def test_create_device_duplicate_device_id(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test device creation with duplicate device_id returns conflict error."""
        # Create first device
        response1 = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert response1.status_code == 201
        
        # Attempt to create device with same device_id
        response2 = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert response2.status_code == 409
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()
        assert sample_device_data["device_id"] in error_data["detail"]

    @pytest.mark.asyncio
    async def test_get_devices_list_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any],
        inactive_device_data: Dict[str, Any]
    ):
        """Test successful retrieval of devices list with pagination and filtering."""
        # Create multiple devices
        await async_client.post("/api/v1/devices/", json=sample_device_data)
        await async_client.post("/api/v1/devices/", json=inactive_device_data)
        
        # Retrieve all devices
        response = await async_client.get("/api/v1/devices/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Test pagination
        response_paginated = await async_client.get("/api/v1/devices/?skip=0&limit=1")
        assert response_paginated.status_code == 200
        paginated_data = response_paginated.json()
        assert len(paginated_data) == 1
        
        # Test filtering by active status
        response_active = await async_client.get("/api/v1/devices/?is_active=true")
        assert response_active.status_code == 200
        active_data = response_active.json()
        assert all(device["is_active"] for device in active_data)
        
        # Test filtering by connection type
        response_conn_type = await async_client.get("/api/v1/devices/?connection_type=USB")
        assert response_conn_type.status_code == 200
        conn_type_data = response_conn_type.json()
        assert all(device["last_connection_type"] == "USB" for device in conn_type_data)
        assert any(device["device_id"] == sample_device_data["device_id"] for device in conn_type_data)
        
    @pytest.mark.asyncio
    async def test_get_devices_list_pagination_order(
        self,
        async_client: AsyncClient,
        test_db_session: Session
    ):
        """Test that the device list is paginated correctly and maintains expected order."""
        # Create multiple devices with different connection types
        devices_to_create = [
            {
                "device_id": f"test-device-order-{i}",
                "name": f"Test Device {i}",
                "model": f"Test Model {i}",
                "manufacturer": "Test Manufacturer",
                "android_version": "11.0",
                "app_version": "1.2.3",
                "supports_nfc": True,
                "supports_ndef": True,
                "is_active": i % 2 == 0,  # Even indices are active, odd are inactive
                "last_connection_type": ["USB", "WiFi", "Bluetooth"][i % 3],
                "device_info": {"cpu": "octa-core", "ram": "8GB"},
                "notes": f"Test device {i} for pagination testing"
            }
            for i in range(5)  # Create 5 devices
        ]
        
        # Create the devices
        device_ids = []
        for device_data in devices_to_create:
            response = await async_client.post("/api/v1/devices/", json=device_data)
            assert response.status_code == 201
            device_ids.append(response.json()["id"])
        
        # Test pagination with different skip and limit values
        response = await async_client.get("/api/v1/devices/?skip=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Test that we get different devices when changing pagination
        response_next_page = await async_client.get("/api/v1/devices/?skip=3&limit=2")
        assert response_next_page.status_code == 200
        next_page_data = response_next_page.json()
        assert len(next_page_data) == 2
        
        # Verify different sets of devices are returned
        first_page_ids = [device["device_id"] for device in data]
        second_page_ids = [device["device_id"] for device in next_page_data]
        assert set(first_page_ids) != set(second_page_ids)
        
        # Test combined filtering (both is_active and connection_type)
        response_filtered = await async_client.get("/api/v1/devices/?is_active=true&connection_type=USB")
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        assert all(device["is_active"] for device in filtered_data)
        assert all(device["last_connection_type"] == "USB" for device in filtered_data)

    @pytest.mark.asyncio
    async def test_get_device_by_id_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test successful retrieval of a device by ID."""
        # Create device first
        create_response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert create_response.status_code == 201
        device_id = create_response.json()["id"]
        
        # Retrieve device
        response = await async_client.get(f"/api/v1/devices/{device_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == device_id
        assert data["device_id"] == sample_device_data["device_id"]
        assert data["name"] == sample_device_data["name"]

    @pytest.mark.asyncio
    async def test_get_device_by_id_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent device returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/v1/devices/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_device_by_device_id_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test successful retrieval of a device by device_id."""
        # Create device first
        create_response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert create_response.status_code == 201
        
        # Retrieve device by device_id
        device_id = sample_device_data["device_id"]
        response = await async_client.get(f"/api/v1/devices/by-device-id/{device_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["device_id"] == device_id
        assert data["name"] == sample_device_data["name"]

    @pytest.mark.asyncio
    async def test_get_device_by_device_id_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent device_id returns 404."""
        response = await async_client.get("/api/v1/devices/by-device-id/nonexistent_device_id")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_device_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test successful device update."""
        # Create device first
        create_response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert create_response.status_code == 201
        device_id = create_response.json()["id"]
        
        # Update device
        update_data = {
            "name": "Updated Device Name",
            "model": "Updated Model",
            "app_version": "1.3.0",
            "notes": "Updated notes",
            "device_info": {"cpu": "octa-core", "ram": "16GB", "storage": "256GB"}
        }
        
        response = await async_client.put(f"/api/v1/devices/{device_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == device_id
        assert data["name"] == update_data["name"]
        assert data["model"] == update_data["model"]
        assert data["app_version"] == update_data["app_version"]
        assert data["notes"] == update_data["notes"]
        assert data["device_info"] == update_data["device_info"]
        
        # Verify device_id remained unchanged
        assert data["device_id"] == sample_device_data["device_id"]
        
        # Verify changes were persisted in database
        db_device = test_db_session.query(Device).filter(Device.id == uuid.UUID(device_id)).first()
        assert db_device is not None
        assert db_device.name == update_data["name"]
        assert db_device.model == update_data["model"]
        assert db_device.app_version == update_data["app_version"]
        assert db_device.notes == update_data["notes"]
        assert db_device.device_info == update_data["device_info"]

    @pytest.mark.asyncio
    async def test_update_device_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test update of non-existent device returns 404."""
        non_existent_id = str(uuid.uuid4())
        update_data = {"name": "Should not work"}
        
        response = await async_client.put(f"/api/v1/devices/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_device_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test successful device deletion."""
        # Create device first
        create_response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert create_response.status_code == 201
        device_id = create_response.json()["id"]
        device_string_id = sample_device_data["device_id"]
        
        # Verify device exists in database before deletion
        db_device = test_db_session.query(Device).filter(Device.id == uuid.UUID(device_id)).first()
        assert db_device is not None
        
        # Delete device
        response = await async_client.delete(f"/api/v1/devices/{device_id}")
        assert response.status_code == 204
        
        # Verify device is deleted from database
        db_device_after = test_db_session.query(Device).filter(Device.id == uuid.UUID(device_id)).first()
        assert db_device_after is None
        
        # Verify device is not found via UUID API
        get_response = await async_client.get(f"/api/v1/devices/{device_id}")
        assert get_response.status_code == 404
        
        # Verify device is not found via device_id API
        get_by_device_id_response = await async_client.get(f"/api/v1/devices/by-device-id/{device_string_id}")
        assert get_by_device_id_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_device_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test deletion of non-existent device returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.delete(f"/api/v1/devices/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest.mark.asyncio
    async def test_activate_deactivate_device(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_device_data: Dict[str, Any]
    ):
        """Test activating and deactivating a device."""
        # Create device first with inactive status
        sample_device_data["is_active"] = False
        create_response = await async_client.post("/api/v1/devices/", json=sample_device_data)
        assert create_response.status_code == 201
        device_id = create_response.json()["id"]
        assert create_response.json()["is_active"] is False
        
        # Activate device
        activate_response = await async_client.patch(f"/api/v1/devices/{device_id}/activate")
        assert activate_response.status_code == 200
        assert activate_response.json()["is_active"] is True
        
        # Verify activation status in database
        device = test_db_session.query(Device).filter(Device.id == uuid.UUID(device_id)).first()
        assert device is not None
        assert device.is_active is True
        
        # Deactivate device
        deactivate_response = await async_client.patch(f"/api/v1/devices/{device_id}/deactivate")
        assert deactivate_response.status_code == 200
        assert deactivate_response.json()["is_active"] is False
        
        # Verify deactivation status in database
        test_db_session.refresh(device)
        assert device.is_active is False
    
    @pytest.mark.asyncio
    async def test_activate_deactivate_device_not_found(
        self,
        async_client: AsyncClient
    ):
        """Test activation/deactivation of non-existent device returns 404."""
        non_existent_id = str(uuid.uuid4())
        
        # Attempt to activate non-existent device
        activate_response = await async_client.patch(f"/api/v1/devices/{non_existent_id}/activate")
        assert activate_response.status_code == 404
        error_data = activate_response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
        
        # Attempt to deactivate non-existent device
        deactivate_response = await async_client.patch(f"/api/v1/devices/{non_existent_id}/deactivate")
        assert deactivate_response.status_code == 404
        error_data = deactivate_response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()
