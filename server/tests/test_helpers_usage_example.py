"""
Example usage of test helpers for the NFC Reader/Writer System PC Server.

This module demonstrates how to use the helper functions to create test resources
quickly via ORM when routes under test require existing resources.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

from server.tests.conftest import async_client, test_db_session
from server.db.models.device import Device

from server.tests.test_helpers import (
    create_test_user,
    create_test_device,
    create_test_connection,
    create_test_nfc_tag,
    create_test_nfc_record,
    create_related_resources,
)


class TestHelperUsageExamples:
    """Examples of how to use the test helpers in actual tests."""

    @pytest.mark.asyncio
    async def test_connection_with_existing_resources(self, async_client: AsyncClient, test_db_session: Session):
        """
        Example: Testing connection creation when we need existing user and device.
        
        This demonstrates how to use the helpers to quickly create the resources
        needed for the test directly via ORM, rather than making HTTP requests.
        """
        # Create necessary resources directly via ORM
        user = create_test_user(test_db_session, username="connection_test_user")
        device = create_test_device(test_db_session, name="Connection Test Device")
        
        # Now test the connection endpoint with these existing resources
        connection_data = {
            "connection_type": "WiFi",
            "connected_at": "2023-06-26T10:30:00",
            "is_active": True,
            "ip_address": "192.168.1.150",
            "port": "8080",
            "device_id": str(device.id),
            "user_id": str(user.id),
            "connection_info": {"wifi_security": "WPA2"},
            "notes": "Test connection with existing resources"
        }
        
        # Make the actual API call we're testing
        response = await async_client.post("/api/v1/connections/", json=connection_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["device_id"] == str(device.id)
        assert data["user_id"] == str(user.id)

    @pytest.mark.asyncio
    async def test_using_related_resources_helper(self, async_client: AsyncClient, test_db_session: Session):
        """
        Example: Using the create_related_resources helper to create multiple related resources at once.
        
        This is useful when testing complex scenarios that require a complete set of resources.
        """
        # Create all related resources in a single call
        resources = create_related_resources(
            test_db_session,
            create_user=True,
            create_device=True,
            create_connection=True,
            create_tag=True,
            create_record=True
        )
        
        # Now you can use these resources in your test
        user = resources["user"]
        device = resources["device"]
        connection = resources["connection"]
        tag = resources["tag"]
        record = resources["record"]
        
        # Skip direct API testing - just verify resources were created
        assert user is not None
        assert device is not None
        assert connection is not None
        assert tag is not None
        assert record is not None
        
        # Check the relationships
        assert connection.device_id == device.id
        assert record.tag_id == tag.id
        assert tag.device_id == device.id
        
    @pytest.mark.asyncio
    async def test_using_resources_without_http_roundtrip(self, test_db_session: Session):
        """
        Example: Testing validator logic directly without HTTP round-trips.
        
        This demonstrates how to test validation logic directly by working
        with the database session, which is faster than making HTTP requests.
        """
        # We'll define a simple validator function for testing
        def validate_connection_creation(db, data):
            # Simple validation function for testing
            device_id = data.get("device_id")
            device = db.query(Device).filter(Device.id == device_id).first()
            
            # Return a structure similar to what a real validator would return
            return {
                "is_valid": True if device else False,
                "validated_data": {
                    "device": device,
                    "connection_type": data.get("connection_type"),
                    "is_active": data.get("is_active", True)
                }
            }
        
        # Create resources needed for the test
        device = create_test_device(test_db_session)
        
        # Test the validator directly
        connection_data = {
            "connection_type": "USB",
            "device_id": device.id,  # Can use the actual UUID object
            "user_id": None,
            "is_active": True,
        }
        
        # Call the validator directly
        # This is faster than making an HTTP request and still tests the validation logic
        result = validate_connection_creation(test_db_session, connection_data)
        
        # Assertions
        assert result["is_valid"] is True
        assert "device" in result["validated_data"]
        assert result["validated_data"]["device"].id == device.id

    @pytest.mark.asyncio
    async def test_batch_resource_creation(self, test_db_session: Session):
        """
        Example: Creating multiple resources for bulk operation testing.
        
        This demonstrates how to efficiently create multiple resources for
        testing endpoints that deal with bulk operations.
        """
        # Create a device to associate with multiple tags
        device = create_test_device(test_db_session)
        
        # Create multiple NFC tags for the same device
        tags = []
        for i in range(5):
            tag = create_test_nfc_tag(
                test_db_session,
                device=device,
                uid=f"04A{i}B{i}C{i}D{i}E{i}F{i}",
                notes=f"Batch tag {i}",
                commit=True  # Commit each one to get the ID
            )
            tags.append(tag)
        
        # Now test operations on these tags
        # For example, verify we can query all tags for this device
        from server.db.models.nfc_tag import NFCTag
        device_tags = test_db_session.query(NFCTag).filter(NFCTag.device_id == device.id).all()
        
        # Assertions
        assert len(device_tags) == 5
        tag_ids = [tag.id for tag in tags]
        device_tag_ids = [tag.id for tag in device_tags]
        assert set(tag_ids) == set(device_tag_ids)
