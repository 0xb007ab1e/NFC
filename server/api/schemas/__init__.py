"""
API schemas for the NFC Reader/Writer System PC Server.

This package contains Pydantic models for API request and response validation.
"""

from server.api.schemas.nfc import NFCTagCreate, NFCTagResponse, NFCRecordCreate, NFCRecordResponse
from server.api.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from server.api.schemas.connection import ConnectionCreate, ConnectionResponse, ConnectionUpdate
from server.api.schemas.user import UserCreate, UserResponse, UserUpdate

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
