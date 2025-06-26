import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import the main FastAPI app
from server.api.app import app

# Import your database configuration and models
from server.db.config import Base
from server.db.models import NFCTag, NFCRecord, Device, Connection, User


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def test_db_session() -> Session:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)

@pytest_asyncio.fixture
async def async_client():
    """Create an async test client."""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient
    
    # Use the regular TestClient approach for now
    test_client = TestClient(app)
    
    # For async testing, we need to use AsyncClient differently
    transport = test_client._transport
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Create a TestClient alias for backward compatibility
TestClient = AsyncClient

# Test data fixtures
@pytest.fixture
def sample_tag_data():
    """Sample NFC tag data for testing."""
    from datetime import datetime
    import uuid
    from server.api.schemas.nfc import NFCTagType
    
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
def sample_record_data():
    """Sample NFC record data for testing."""
    from server.api.schemas.nfc import TNFType
    
    return {
        "tnf": TNFType.WELL_KNOWN.value,
        "type": "T",
        "payload_str": "Hello, World!",
        "record_index": 0,
        "parsed_data": {"text": "Hello, World!", "language": "en"}
    }
