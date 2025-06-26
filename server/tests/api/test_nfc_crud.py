"""
NFC CRUD API Tests for the NFC Reader/Writer System.

This module contains comprehensive tests for NFC tag and record CRUD operations,
covering happy path scenarios, error cases, and edge conditions.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Test utilities
from server.tests.conftest import TestClient, test_db_session
from server.api.app import app
from server.db.models import NFCTag, NFCRecord
from server.api.schemas.nfc import TNFType, NFCTagType


@pytest.fixture
def sample_tag_data() -> Dict[str, Any]:
    """Sample NFC tag data for testing."""
    return {
        "uid": "04A12B3C4D5E6F",
        "tech_list": ["android.nfc.tech.IsoDep", "android.nfc.tech.NfcA"],
        "tag_type": NFCTagType.TYPE4.value,
        "is_writable": True,
        "is_ndef_formatted": True,
        "max_size": 8192,
        "read_timestamp": datetime.now().isoformat(),
        "read_location": {"latitude": 37.7749, "longitude": -122.4194},
        "device_id": str(uuid.uuid4()),
        "notes": "Test NFC tag for unit testing",
        "custom_data": {"test_field": "test_value"},
        "records": []
    }


@pytest.fixture
def sample_record_data() -> Dict[str, Any]:
    """Sample NFC record data for testing."""
    return {
        "tnf": TNFType.WELL_KNOWN.value,
        "type": "T",
        "payload_str": "Hello, World!",
        "record_index": 0,
        "parsed_data": {"text": "Hello, World!", "language": "en"}
    }


@pytest.fixture
def sample_uri_record_data() -> Dict[str, Any]:
    """Sample URI NFC record data for testing."""
    return {
        "tnf": TNFType.ABSOLUTE_URI.value,
        "type": "U",
        "payload_str": "https://example.com",
        "record_index": 0,
        "parsed_data": {"uri": "https://example.com"}
    }


class TestNFCTagCRUD:
    """Test cases for NFC Tag CRUD operations."""

    @pytest_asyncio.async_test
    async def test_create_nfc_tag_success(
        self, 
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test successful NFC tag creation (happy path)."""
        response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["uid"] == sample_tag_data["uid"]
        assert data["tech_list"] == sample_tag_data["tech_list"]
        assert data["tag_type"] == sample_tag_data["tag_type"]
        assert data["is_writable"] == sample_tag_data["is_writable"]
        assert data["is_ndef_formatted"] == sample_tag_data["is_ndef_formatted"]
        assert data["max_size"] == sample_tag_data["max_size"]
        assert data["device_id"] == sample_tag_data["device_id"]
        assert data["notes"] == sample_tag_data["notes"]
        assert data["custom_data"] == sample_tag_data["custom_data"]
        
        # Verify database entry
        tag_id = uuid.UUID(data["id"])
        db_tag = test_db_session.query(NFCTag).filter(NFCTag.id == tag_id).first()
        assert db_tag is not None
        assert db_tag.uid == sample_tag_data["uid"]

    @pytest_asyncio.async_test
    async def test_create_nfc_tag_duplicate_uid_conflict(
        self, 
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test duplicate NFC tag UID returns 409 Conflict."""
        # Create first tag
        response1 = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert response1.status_code == 201
        
        # Attempt to create tag with same UID
        response2 = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert response2.status_code == 409
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()
        assert sample_tag_data["uid"] in error_data["detail"]

    @pytest_asyncio.async_test
    async def test_create_nfc_tag_with_records(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any],
        sample_record_data: Dict[str, Any]
    ):
        """Test creating NFC tag with embedded records."""
        sample_tag_data["records"] = [sample_record_data]
        
        response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert response.status_code == 201
        
        data = response.json()
        assert len(data["records"]) == 1
        assert data["records"][0]["tnf"] == sample_record_data["tnf"]
        assert data["records"][0]["type"] == sample_record_data["type"]
        assert data["records"][0]["payload_str"] == sample_record_data["payload_str"]

    @pytest_asyncio.async_test
    async def test_get_nfc_tag_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test successful retrieval of a single NFC tag."""
        # Create tag first
        create_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert create_response.status_code == 201
        tag_id = create_response.json()["id"]
        
        # Retrieve tag
        response = await async_client.get(f"/api/nfc/tags/{tag_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == tag_id
        assert data["uid"] == sample_tag_data["uid"]

    @pytest_asyncio.async_test
    async def test_get_nonexistent_nfc_tag_404(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent NFC tag returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/nfc/tags/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest_asyncio.async_test
    async def test_get_nfc_tags_list_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test successful retrieval of NFC tags list with pagination."""
        # Create multiple tags
        tag_count = 3
        created_tags = []
        
        for i in range(tag_count):
            tag_data = sample_tag_data.copy()
            tag_data["uid"] = f"04A12B3C4D5E{i:02X}"
            tag_data["notes"] = f"Test tag {i}"
            
            response = await async_client.post("/api/nfc/tags", json=tag_data)
            assert response.status_code == 201
            created_tags.append(response.json())
        
        # Retrieve tags list
        response = await async_client.get("/api/nfc/tags")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= tag_count
        
        # Verify pagination
        response_paginated = await async_client.get("/api/nfc/tags?skip=0&limit=2")
        assert response_paginated.status_code == 200
        paginated_data = response_paginated.json()
        assert len(paginated_data) <= 2

    @pytest_asyncio.async_test
    async def test_update_nfc_tag_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test successful NFC tag update."""
        # Create tag first
        create_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert create_response.status_code == 201
        tag_id = create_response.json()["id"]
        
        # Update tag
        update_data = {
            "is_writable": False,
            "notes": "Updated test notes",
            "custom_data": {"updated_field": "updated_value"}
        }
        
        response = await async_client.put(f"/api/nfc/tags/{tag_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == tag_id
        assert data["is_writable"] == update_data["is_writable"]
        assert data["notes"] == update_data["notes"]
        assert data["custom_data"] == update_data["custom_data"]

    @pytest_asyncio.async_test
    async def test_update_nonexistent_nfc_tag_404(
        self,
        async_client: AsyncClient
    ):
        """Test update of non-existent NFC tag returns 404."""
        non_existent_id = str(uuid.uuid4())
        update_data = {"notes": "Should not work"}
        
        response = await async_client.put(f"/api/nfc/tags/{non_existent_id}", json=update_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest_asyncio.async_test
    async def test_delete_nfc_tag_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test successful NFC tag deletion."""
        # Create tag first
        create_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert create_response.status_code == 201
        tag_id = create_response.json()["id"]
        
        # Delete tag
        response = await async_client.delete(f"/api/nfc/tags/{tag_id}")
        assert response.status_code == 204
        
        # Verify tag is deleted
        get_response = await async_client.get(f"/api/nfc/tags/{tag_id}")
        assert get_response.status_code == 404

    @pytest_asyncio.async_test
    async def test_delete_nonexistent_nfc_tag_404(
        self,
        async_client: AsyncClient
    ):
        """Test deletion of non-existent NFC tag returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.delete(f"/api/nfc/tags/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest_asyncio.async_test
    async def test_delete_nfc_tag_with_records_cascades(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any],
        sample_record_data: Dict[str, Any]
    ):
        """Test that deleting an NFC tag cascades to delete its records."""
        # Create tag with record
        sample_tag_data["records"] = [sample_record_data]
        create_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert create_response.status_code == 201
        
        tag_data = create_response.json()
        tag_id = tag_data["id"]
        record_id = tag_data["records"][0]["id"]
        
        # Verify record exists
        record_response = await async_client.get(f"/api/nfc/records/{record_id}")
        assert record_response.status_code == 200
        
        # Delete tag
        delete_response = await async_client.delete(f"/api/nfc/tags/{tag_id}")
        assert delete_response.status_code == 204
        
        # Verify record is also deleted (cascade)
        record_check = await async_client.get(f"/api/nfc/records/{record_id}")
        assert record_check.status_code == 404


class TestNFCRecordOperations:
    """Test cases for NFC Record operations."""

    @pytest_asyncio.async_test
    async def test_create_nfc_record_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any],
        sample_record_data: Dict[str, Any]
    ):
        """Test successful NFC record creation (happy path)."""
        # Create tag first
        tag_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]
        
        # Add tag_id to record data
        sample_record_data["tag_id"] = tag_id
        
        # Create record
        response = await async_client.post("/api/nfc/records", json=sample_record_data)
        assert response.status_code == 201
        
        data = response.json()
        assert "id" in data
        assert data["tnf"] == sample_record_data["tnf"]
        assert data["type"] == sample_record_data["type"]
        assert data["payload_str"] == sample_record_data["payload_str"]
        assert data["tag_id"] == tag_id
        assert data["record_index"] == sample_record_data["record_index"]

    @pytest_asyncio.async_test
    async def test_create_nfc_record_nonexistent_tag_404(
        self,
        async_client: AsyncClient,
        sample_record_data: Dict[str, Any]
    ):
        """Test creating NFC record with non-existent tag returns 404."""
        non_existent_tag_id = str(uuid.uuid4())
        sample_record_data["tag_id"] = non_existent_tag_id
        
        response = await async_client.post("/api/nfc/records", json=sample_record_data)
        assert response.status_code == 404
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest_asyncio.async_test
    async def test_get_nfc_record_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any],
        sample_record_data: Dict[str, Any]
    ):
        """Test successful retrieval of a single NFC record."""
        # Create tag first
        tag_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]
        
        # Create record
        sample_record_data["tag_id"] = tag_id
        record_response = await async_client.post("/api/nfc/records", json=sample_record_data)
        assert record_response.status_code == 201
        record_id = record_response.json()["id"]
        
        # Retrieve record
        response = await async_client.get(f"/api/nfc/records/{record_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == record_id
        assert data["tnf"] == sample_record_data["tnf"]
        assert data["type"] == sample_record_data["type"]

    @pytest_asyncio.async_test
    async def test_get_nonexistent_nfc_record_404(
        self,
        async_client: AsyncClient
    ):
        """Test retrieval of non-existent NFC record returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/nfc/records/{non_existent_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    @pytest_asyncio.async_test
    async def test_get_records_for_tag_success(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any],
        sample_record_data: Dict[str, Any],
        sample_uri_record_data: Dict[str, Any]
    ):
        """Test successful retrieval of all records for a specific tag."""
        # Create tag first
        tag_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]
        
        # Create multiple records
        sample_record_data["tag_id"] = tag_id
        sample_uri_record_data["tag_id"] = tag_id
        sample_uri_record_data["record_index"] = 1
        
        record1_response = await async_client.post("/api/nfc/records", json=sample_record_data)
        assert record1_response.status_code == 201
        
        record2_response = await async_client.post("/api/nfc/records", json=sample_uri_record_data)
        assert record2_response.status_code == 201
        
        # Retrieve all records for tag
        response = await async_client.get(f"/api/nfc/tags/{tag_id}/records")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify records are sorted by record_index
        assert data[0]["record_index"] <= data[1]["record_index"]

    @pytest_asyncio.async_test
    async def test_get_records_for_nonexistent_tag_404(
        self,
        async_client: AsyncClient
    ):
        """Test retrieving records for non-existent tag returns 404."""
        non_existent_tag_id = str(uuid.uuid4())
        response = await async_client.get(f"/api/nfc/tags/{non_existent_tag_id}/records")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()


class TestNFCValidationAndEdgeCases:
    """Test cases for validation and edge cases."""

    @pytest_asyncio.async_test
    async def test_create_tag_invalid_uid_format(
        self,
        async_client: AsyncClient,
        sample_tag_data: Dict[str, Any]
    ):
        """Test creating tag with invalid UID format returns validation error."""
        sample_tag_data["uid"] = "invalid-uid-format"
        
        response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert response.status_code == 422  # Validation error
        
        error_data = response.json()
        assert "detail" in error_data

    @pytest_asyncio.async_test
    async def test_create_tag_missing_required_fields(
        self,
        async_client: AsyncClient
    ):
        """Test creating tag with missing required fields returns validation error."""
        incomplete_data = {
            "uid": "04A12B3C4D5E6F",
            # Missing required fields like tech_list, tag_type, etc.
        }
        
        response = await async_client.post("/api/nfc/tags", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    @pytest_asyncio.async_test
    async def test_create_record_invalid_tnf(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test creating record with invalid TNF value returns validation error."""
        # Create tag first
        tag_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]
        
        invalid_record_data = {
            "tnf": 999,  # Invalid TNF value
            "type": "T",
            "payload_str": "Test",
            "record_index": 0,
            "tag_id": tag_id
        }
        
        response = await async_client.post("/api/nfc/records", json=invalid_record_data)
        assert response.status_code == 422  # Validation error

    @pytest_asyncio.async_test
    async def test_create_tag_with_empty_tech_list(
        self,
        async_client: AsyncClient,
        sample_tag_data: Dict[str, Any]
    ):
        """Test creating tag with empty tech_list returns validation error."""
        sample_tag_data["tech_list"] = []
        
        response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert response.status_code == 422  # Validation error

    @pytest_asyncio.async_test
    async def test_large_payload_handling(
        self,
        async_client: AsyncClient,
        test_db_session: Session,
        sample_tag_data: Dict[str, Any]
    ):
        """Test handling of large record payloads."""
        # Create tag first
        tag_response = await async_client.post("/api/nfc/tags", json=sample_tag_data)
        assert tag_response.status_code == 201
        tag_id = tag_response.json()["id"]
        
        large_record_data = {
            "tnf": TNFType.WELL_KNOWN.value,
            "type": "T",
            "payload_str": "x" * 9999,  # Large payload (within limit)
            "record_index": 0,
            "tag_id": tag_id,
            "parsed_data": {"text": "x" * 9999}
        }
        
        response = await async_client.post("/api/nfc/records", json=large_record_data)
        assert response.status_code == 201

    @pytest_asyncio.async_test
    async def test_concurrent_tag_creation_race_condition(
        self,
        async_client: AsyncClient,
        sample_tag_data: Dict[str, Any]
    ):
        """Test handling of concurrent tag creation with same UID."""
        import asyncio
        
        # Create tasks that attempt to create the same tag simultaneously
        tasks = [
            async_client.post("/api/nfc/tags", json=sample_tag_data)
            for _ in range(3)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # One should succeed (201), others should fail with 409 or 500
        success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 201)
        conflict_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 409)
        
        assert success_count == 1
        assert conflict_count >= 1

    @pytest_asyncio.async_test
    async def test_tag_with_gps_coordinates_boundary_values(
        self,
        async_client: AsyncClient,
        sample_tag_data: Dict[str, Any]
    ):
        """Test tag creation with boundary GPS coordinate values."""
        test_cases = [
            {"latitude": 90.0, "longitude": 180.0},    # Max valid values
            {"latitude": -90.0, "longitude": -180.0},  # Min valid values
            {"latitude": 0.0, "longitude": 0.0},       # Zero values
        ]
        
        for i, coords in enumerate(test_cases):
            tag_data = sample_tag_data.copy()
            tag_data["uid"] = f"04A12B3C4D5E{i:02X}"
            tag_data["read_location"] = coords
            
            response = await async_client.post("/api/nfc/tags", json=tag_data)
            assert response.status_code == 201
            
            data = response.json()
            assert data["read_location"] == coords
