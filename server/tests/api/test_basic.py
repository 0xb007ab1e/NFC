"""
Basic API tests for the NFC server.
"""
import pytest
from fastapi.testclient import TestClient

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now import app
from api.app import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint returns OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
