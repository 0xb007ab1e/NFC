"""
Basic API tests for the NFC server.
"""
import pytest
from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint returns OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
