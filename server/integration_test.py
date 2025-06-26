#!/usr/bin/env python3
"""
Integration Test Script for NFC API

This script provides manual integration testing for the NFC Tap-to-Connect API endpoints.
It tests the main functionality without requiring complex async test setup.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

import httpx
import uvicorn
from multiprocessing import Process

# Import the FastAPI app
from api.app import app
from db.config import init_db


def start_test_server():
    """Start the test server in a separate process."""
    # Initialize the database
    init_db()
    
    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    
    try:
        response = httpx.get("http://127.0.0.1:8000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False


def test_nfc_tag_operations():
    """Test NFC tag CRUD operations."""
    print("Testing NFC tag operations...")
    
    # Sample tag data
    tag_data = {
        "uid": "04A12B3C4D5E6F",
        "tech_list": ["android.nfc.tech.IsoDep", "android.nfc.tech.NfcA"],
        "tag_type": "TYPE4",
        "is_writable": True,
        "is_ndef_formatted": True,
        "max_size": 8192,
        "read_timestamp": datetime.now().isoformat(),
        "read_location": {"latitude": 37.7749, "longitude": -122.4194},
        "device_id": "test-device-123",
        "notes": "Integration test NFC tag",
        "custom_data": {"test": "integration_test"},
        "records": []
    }
    
    try:
        # Test creating tag
        response = httpx.post("http://127.0.0.1:8000/api/nfc/tags", json=tag_data)
        if response.status_code != 201:
            print(f"❌ Create tag failed: {response.status_code}, {response.text}")
            return False
        
        created_tag = response.json()
        tag_id = created_tag["id"]
        print(f"✅ Created tag with ID: {tag_id}")
        
        # Test getting tag
        response = httpx.get(f"http://127.0.0.1:8000/api/nfc/tags/{tag_id}")
        if response.status_code != 200:
            print(f"❌ Get tag failed: {response.status_code}")
            return False
        
        retrieved_tag = response.json()
        assert retrieved_tag["uid"] == tag_data["uid"]
        print("✅ Retrieved tag successfully")
        
        # Test updating tag
        update_data = {"notes": "Updated integration test tag"}
        response = httpx.put(f"http://127.0.0.1:8000/api/nfc/tags/{tag_id}", json=update_data)
        if response.status_code != 200:
            print(f"❌ Update tag failed: {response.status_code}")
            return False
        
        updated_tag = response.json()
        assert updated_tag["notes"] == update_data["notes"]
        print("✅ Updated tag successfully")
        
        # Test listing tags
        response = httpx.get("http://127.0.0.1:8000/api/nfc/tags")
        if response.status_code != 200:
            print(f"❌ List tags failed: {response.status_code}")
            return False
        
        tags_list = response.json()
        assert isinstance(tags_list, list)
        assert len(tags_list) >= 1
        print("✅ Listed tags successfully")
        
        # Test deleting tag
        response = httpx.delete(f"http://127.0.0.1:8000/api/nfc/tags/{tag_id}")
        if response.status_code != 204:
            print(f"❌ Delete tag failed: {response.status_code}")
            return False
        
        print("✅ Deleted tag successfully")
        
        # Verify tag is deleted
        response = httpx.get(f"http://127.0.0.1:8000/api/nfc/tags/{tag_id}")
        if response.status_code != 404:
            print(f"❌ Tag should be deleted but still exists")
            return False
        
        print("✅ Verified tag deletion")
        return True
        
    except Exception as e:
        print(f"❌ NFC tag operations test failed: {e}")
        return False


def test_validation_errors():
    """Test API validation error handling."""
    print("Testing validation error handling...")
    
    try:
        # Test invalid tag data
        invalid_tag = {
            "uid": "invalid_uid",  # Should be hex
            "tech_list": [],  # Should not be empty
            "tag_type": "INVALID_TYPE",  # Invalid enum
        }
        
        response = httpx.post("http://127.0.0.1:8000/api/nfc/tags", json=invalid_tag)
        if response.status_code != 422:
            print(f"❌ Expected validation error (422) but got: {response.status_code}")
            return False
        
        error_data = response.json()
        assert "detail" in error_data
        print("✅ Validation error handling works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Validation error test failed: {e}")
        return False


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting NFC API Integration Tests")
    print("=" * 50)
    
    # Start server in background process
    server_process = Process(target=start_test_server)
    server_process.start()
    
    try:
        # Wait for server to start
        print("Waiting for server to start...")
        time.sleep(3)
        
        # Check if server is ready
        ready = False
        for i in range(10):
            try:
                response = httpx.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if not ready:
            print("❌ Server failed to start")
            return False
        
        print("✅ Server is ready")
        print()
        
        # Run tests
        tests = [
            test_health_endpoint,
            test_nfc_tag_operations,
            test_validation_errors,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()
        
        # Print summary
        print("=" * 50)
        print(f"Integration Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All integration tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False
        
    finally:
        # Clean up server process
        server_process.terminate()
        server_process.join()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
