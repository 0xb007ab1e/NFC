"""
API schemas for the NFC Reader/Writer System PC Server.

This package contains Pydantic models for API request and response validation.
"""

from server.api.schemas.nfc import NFCTagCreate, NFCTagResponse, NFCRecordCreate, NFCRecordResponse

try:
    from server.api.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate, DeviceListResponse
    from server.api.schemas.connection import ConnectionCreate, ConnectionResponse, ConnectionUpdate, ConnectionListResponse, ConnectionCloseRequest
    from server.api.schemas.user import UserCreate, UserResponse, UserUpdate, UserPasswordUpdate, UserListResponse, UserLoginRequest, UserLoginResponse
except ImportError:
    # Fallback for any missing schemas
    pass

__all__ = [
    "NFCTagCreate",
    "NFCTagResponse",
    "NFCRecordCreate",
    "NFCRecordResponse",
    "DeviceCreate",
    "DeviceResponse",
    "DeviceUpdate",
    "ConnectionCreate",
    "ConnectionResponse",
    "ConnectionUpdate",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
]
