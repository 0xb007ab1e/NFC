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
async def async_client(test_db_session):
    """Create an async test client."""
    from fastapi.testclient import TestClient
    from httpx import AsyncClient, ASGITransport
    from server.api.app import app
    from server.db.config import get_db
    
    # Override the dependency
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use ASGI transport with the FastAPI app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()

# Create a TestClient alias for backward compatibility
TestClient = AsyncClient

@pytest.fixture
def test_device(test_db_session):
    """Create a test device for testing."""
    from server.db.models import Device
    import uuid
    from datetime import datetime
    
    device = Device(
        name="Test Device",
        description="Test device for NFC testing",
        device_type="mobile",
        platform="android",
        version="1.0.0",
        last_seen=datetime.now(),
        is_active=True
    )
    test_db_session.add(device)
    test_db_session.commit()
    test_db_session.refresh(device)
    return device

# Test data fixtures
@pytest.fixture
def sample_tag_data(test_device):
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
        "device_id": str(test_device.id),
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


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "is_active": True,
        "is_admin": False,
        "permissions": ["read", "write"],
        "first_name": "Test",
        "last_name": "User",
        "notes": "Test user for unit testing",
        "user_metadata": {"department": "Testing"}
    }


@pytest.fixture
def admin_user_data():
    """Sample admin user data for testing."""
    return {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "is_active": True,
        "is_admin": True,
        "permissions": ["read", "write", "admin"],
        "first_name": "Admin",
        "last_name": "User",
        "notes": "Admin user for testing",
        "user_metadata": {"department": "Administration"}
    }
