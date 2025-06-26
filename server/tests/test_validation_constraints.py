"""
Tests for Pydantic validation constraints and HTTPExceptionFactory.

This module tests the enhanced validation added to schemas and the
standardized error handling using HTTPExceptionFactory.
"""

import pytest
from pydantic import ValidationError
from fastapi import status

from server.api.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from server.api.schemas.device import DeviceCreate, DeviceUpdate, ConnectionType
from server.api.schemas.connection import ConnectionCreate, ConnectionUpdate, ConnectionType as ConnType
from server.api.schemas.nfc import NFCTagCreate, NFCRecordCreate, TNFType, NFCTagType
from server.api.exceptions import HTTPExceptionFactory, ErrorCodes, ValidationExceptionHandler


class TestUserSchemaValidation:
    """Test validation constraints for User schemas."""
    
    def test_username_constraints(self):
        """Test username validation constraints."""
        # Valid username
        user_data = {
            "username": "valid_user123",
            "email": "user@example.com",
            "password": "ValidPass123!"
        }
        user = UserCreate(**user_data)
        assert user.username == "valid_user123"
        
        # Invalid username with special characters
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**{**user_data, "username": "invalid@user"})
        
        errors = exc_info.value.errors()
        # Check that validation failed on the username field
        assert any(error['loc'] == ('username',) for error in errors)
        
        # Username too short
        with pytest.raises(ValidationError):
            UserCreate(**{**user_data, "username": ""})
        
        # Username too long
        with pytest.raises(ValidationError):
            UserCreate(**{**user_data, "username": "a" * 51})
    
    def test_password_constraints(self):
        """Test password validation constraints."""
        base_data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Valid password
        user = UserCreate(**{**base_data, "password": "ValidPass123!"})
        assert user.password == "ValidPass123!"
        
        # Password too short
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "password": "short"})
        
        # Password without uppercase
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "password": "lowercase123!"})
        
        # Password without lowercase
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "password": "UPPERCASE123!"})
        
        # Password without digit
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "password": "NoDigits!"})
    
    def test_optional_field_constraints(self):
        """Test optional field validation constraints."""
        base_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "ValidPass123!"
        }
        
        # Valid optional fields
        user = UserCreate(**{
            **base_data,
            "first_name": "John",
            "last_name": "Doe",
            "notes": "Test user account"
        })
        assert user.first_name == "John"
        
        # First name too long
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "first_name": "a" * 51})
        
        # Notes too long
        with pytest.raises(ValidationError):
            UserCreate(**{**base_data, "notes": "a" * 1001})


class TestDeviceSchemaValidation:
    """Test validation constraints for Device schemas."""
    
    def test_device_id_constraints(self):
        """Test device ID validation constraints."""
        base_data = {
            "name": "Test Device",
            "model": "Model123",
            "manufacturer": "TestCorp",
            "android_version": "11.0",
            "app_version": "1.0.0"
        }
        
        # Valid device ID
        device = DeviceCreate(**{**base_data, "device_id": "device_123"})
        assert device.device_id == "device_123"
        
        # Invalid device ID with special characters
        with pytest.raises(ValidationError):
            DeviceCreate(**{**base_data, "device_id": "device@123"})
    
    def test_version_constraints(self):
        """Test version string validation."""
        base_data = {
            "device_id": "device123",
            "name": "Test Device",
            "model": "Model123",
            "manufacturer": "TestCorp"
        }
        
        # Valid version formats
        device = DeviceCreate(**{
            **base_data,
            "android_version": "11.0.1",
            "app_version": "2.1.0"
        })
        assert device.android_version == "11.0.1"
        
        # Invalid version format
        with pytest.raises(ValidationError):
            DeviceCreate(**{**base_data, "android_version": "invalid_version"})
    
    def test_connection_type_enum(self):
        """Test ConnectionType enum validation."""
        # Valid connection type
        assert ConnectionType.USB == "USB"
        assert ConnectionType.WIFI == "WiFi"
        assert ConnectionType.BLUETOOTH == "Bluetooth"
        
        # Enum should restrict values
        base_data = {
            "device_id": "device123",
            "name": "Test Device",
            "model": "Model123",
            "manufacturer": "TestCorp",
            "android_version": "11.0",
            "app_version": "1.0.0"
        }
        
        device = DeviceCreate(**{
            **base_data,
            "last_connection_type": ConnectionType.USB
        })
        assert device.last_connection_type == ConnectionType.USB


class TestConnectionSchemaValidation:
    """Test validation constraints for Connection schemas."""
    
    def test_ip_address_validation(self):
        """Test IP address validation."""
        from uuid import uuid4
        
        base_data = {
            "connection_type": ConnType.WIFI,
            "connected_at": "2023-01-01T00:00:00",
            "device_id": uuid4()
        }
        
        # Valid IP address
        conn = ConnectionCreate(**{
            **base_data,
            "ip_address": "192.168.1.100",
            "port": 8080
        })
        assert conn.ip_address == "192.168.1.100"
        
        # Invalid IP address
        with pytest.raises(ValidationError):
            ConnectionCreate(**{
                **base_data,
                "ip_address": "999.999.999.999",
                "port": 8080
            })
    
    def test_port_validation(self):
        """Test port number validation."""
        from uuid import uuid4
        
        base_data = {
            "connection_type": ConnType.WIFI,
            "connected_at": "2023-01-01T00:00:00",
            "device_id": uuid4(),
            "ip_address": "192.168.1.100"
        }
        
        # Valid port
        conn = ConnectionCreate(**{**base_data, "port": 8080})
        assert conn.port == 8080
        
        # Port too high
        with pytest.raises(ValidationError):
            ConnectionCreate(**{**base_data, "port": 70000})
        
        # Port too low
        with pytest.raises(ValidationError):
            ConnectionCreate(**{**base_data, "port": 0})
    
    def test_conditional_validation(self):
        """Test conditional field validation based on connection type."""
        from uuid import uuid4
        
        base_data = {
            "connected_at": "2023-01-01T00:00:00",
            "device_id": uuid4()
        }
        
        # Test that WiFi connection works with IP and port
        conn_wifi = ConnectionCreate(**{
            **base_data,
            "connection_type": ConnType.WIFI,
            "ip_address": "192.168.1.100",
            "port": 8080
        })
        assert conn_wifi.connection_type == ConnType.WIFI
        
        # Test that USB connection works with USB serial
        conn_usb = ConnectionCreate(**{
            **base_data,
            "connection_type": ConnType.USB,
            "usb_serial": "USB123456"
        })
        assert conn_usb.connection_type == ConnType.USB
        
        # Test that Bluetooth connection works without extra fields
        conn_bt = ConnectionCreate(**{
            **base_data,
            "connection_type": ConnType.BLUETOOTH
        })
        assert conn_bt.connection_type == ConnType.BLUETOOTH


class TestNFCSchemaValidation:
    """Test validation constraints for NFC schemas."""
    
    def test_nfc_uid_validation(self):
        """Test NFC UID validation."""
        from uuid import uuid4
        
        base_data = {
            "tech_list": ["NfcA", "Ndef"],
            "tag_type": NFCTagType.TYPE2,
            "read_timestamp": "2023-01-01T00:00:00",
            "device_id": uuid4()
        }
        
        # Valid UID
        tag = NFCTagCreate(**{**base_data, "uid": "04A1B2C3"})
        assert tag.uid == "04A1B2C3"
        
        # Invalid UID (not hex)
        with pytest.raises(ValidationError):
            NFCTagCreate(**{**base_data, "uid": "GGHHIIJJ"})
        
        # UID too short (less than 8 chars)
        with pytest.raises(ValidationError):
            NFCTagCreate(**{**base_data, "uid": "04A1B2"})
    
    def test_tnf_enum_validation(self):
        """Test TNF enum validation."""
        # Valid TNF values
        assert TNFType.EMPTY == 0
        assert TNFType.WELL_KNOWN == 1
        assert TNFType.MEDIA == 2
        
        record = NFCRecordCreate(
            tnf=TNFType.WELL_KNOWN,
            type="T",
            record_index=0
        )
        assert record.tnf == TNFType.WELL_KNOWN
    
    def test_record_index_validation(self):
        """Test record index validation."""
        # Valid record index
        record = NFCRecordCreate(
            tnf=TNFType.WELL_KNOWN,
            type="T",
            record_index=0
        )
        assert record.record_index == 0
        
        # Negative record index should fail
        with pytest.raises(ValidationError):
            NFCRecordCreate(
                tnf=TNFType.WELL_KNOWN,
                type="T",
                record_index=-1
            )


class TestHTTPExceptionFactory:
    """Test HTTPExceptionFactory for standardized error handling."""
    
    def test_not_found_exception(self):
        """Test not found exception creation."""
        exc = HTTPExceptionFactory.not_found("User", "123")
        
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(exc.detail, dict)
        assert exc.detail["detail"] == "User with identifier '123' not found"
        assert exc.detail["code"] == "NOT_FOUND"
        assert exc.detail["status_code"] == status.HTTP_404_NOT_FOUND
    
    def test_duplicate_resource_exception(self):
        """Test duplicate resource exception creation."""
        exc = HTTPExceptionFactory.duplicate_resource("User", "email", "test@example.com")
        
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail["detail"] == "User with email 'test@example.com' already exists"
        assert exc.detail["code"] == "DUPLICATE_RESOURCE"
        assert exc.detail["params"]["resource"] == "User"
        assert exc.detail["params"]["field"] == "email"
        assert exc.detail["params"]["value"] == "test@example.com"
    
    def test_validation_error_conversion(self):
        """Test conversion from Pydantic ValidationError to HTTPException."""
        # Create a validation error
        try:
            UserCreate(username="", email="invalid", password="weak")
        except ValidationError as ve:
            exc = HTTPExceptionFactory.from_validation_error(ve)
            
            assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert exc.detail["detail"] == "Validation failed"
            assert exc.detail["code"] == "VALIDATION_ERROR"
            assert "errors" in exc.detail
            assert len(exc.detail["errors"]) > 0
    
    def test_bad_request_exception(self):
        """Test bad request exception creation."""
        exc = HTTPExceptionFactory.bad_request(
            "Invalid input data",
            code=ErrorCodes.INVALID_INPUT,
            params={"field": "username"}
        )
        
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail["detail"] == "Invalid input data"
        assert exc.detail["code"] == ErrorCodes.INVALID_INPUT
        assert exc.detail["params"]["field"] == "username"
    
    def test_unauthorized_exception(self):
        """Test unauthorized exception creation."""
        exc = HTTPExceptionFactory.unauthorized()
        
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail["detail"] == "Authentication required"
        assert exc.detail["code"] == "UNAUTHORIZED"
        assert exc.headers["WWW-Authenticate"] == "Bearer"
    
    def test_internal_server_error(self):
        """Test internal server error exception creation."""
        exc = HTTPExceptionFactory.internal_server_error(
            "Database connection failed",
            code=ErrorCodes.DATABASE_ERROR
        )
        
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail["detail"] == "Database connection failed"
        assert exc.detail["code"] == ErrorCodes.DATABASE_ERROR


class TestValidationExceptionHandler:
    """Test ValidationExceptionHandler functionality."""
    
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        try:
            UserCreate(username="", email="invalid", password="weak")
        except ValidationError as ve:
            exc = ValidationExceptionHandler.handle_validation_error(ve)
            
            assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert isinstance(exc.detail, dict)
            assert exc.detail["detail"] == "Validation failed"


class TestErrorCodes:
    """Test ErrorCodes constants."""
    
    def test_error_code_constants(self):
        """Test that error codes are properly defined."""
        assert ErrorCodes.NOT_FOUND == "NOT_FOUND"
        assert ErrorCodes.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCodes.DUPLICATE_RESOURCE == "DUPLICATE_RESOURCE"
        assert ErrorCodes.UNAUTHORIZED == "UNAUTHORIZED"
        assert ErrorCodes.INTERNAL_SERVER_ERROR == "INTERNAL_SERVER_ERROR"
        assert ErrorCodes.DATABASE_ERROR == "DATABASE_ERROR"


if __name__ == "__main__":
    pytest.main([__file__])
