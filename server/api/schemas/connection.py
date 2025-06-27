"""
Connection API schemas for the NFC Reader/Writer System PC Server.

This module contains Pydantic models for Connection API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from pydantic import Field, field_validator, constr, conint
from enum import Enum

from server.api.schemas.base import BaseResponse, BaseCreate, BaseUpdate


class ConnectionType(str, Enum):
    """Enum for connection types."""
    USB = "USB"
    WIFI = "WiFi"
    BLUETOOTH = "Bluetooth"


class ConnectionCreate(BaseCreate):
    """Schema for creating a new connection."""
    
    connection_type: ConnectionType = Field(..., description="Connection type (USB, WiFi, etc.)")
    connected_at: datetime = Field(..., description="Connection timestamp")
    is_active: bool = Field(default=True, description="Whether connection is active")
    ip_address: Optional[str] = Field(None, description="IP address (for WiFi connections)", pattern=r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    port: Optional[conint(gt=0, le=65535)] = Field(None, description="Port (for WiFi connections)")
    usb_serial: Optional[constr(min_length=1, max_length=255)] = Field(None, description="USB serial number (for USB connections)")
    device_id: uuid.UUID = Field(..., description="ID of the connected device")
    user_id: Optional[uuid.UUID] = Field(None, description="ID of the authenticated user")
    connection_info: Optional[Dict[str, Any]] = Field(None, description="Additional connection information")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")

    @field_validator('ip_address')
    def validate_ip_address(cls, v, info):
        """Validate IP address is provided for WiFi connections."""
        values = info.data if info else {}
        if values.get('connection_type') == ConnectionType.WIFI and not v:
            raise ValueError('IP address is required for WiFi connections')
        return v
    
    @field_validator('port')
    def validate_port(cls, v, info):
        """Validate port is provided for WiFi connections."""
        values = info.data if info else {}
        if values.get('connection_type') == ConnectionType.WIFI and not v:
            raise ValueError('Port is required for WiFi connections')
        return v
    
    @field_validator('usb_serial')
    def validate_usb_serial(cls, v, info):
        """Validate USB serial is provided for USB connections."""
        values = info.data if info else {}
        if values.get('connection_type') == ConnectionType.USB and not v:
            raise ValueError('USB serial number is required for USB connections')
        return v


class ConnectionUpdate(BaseUpdate):
    """Schema for updating a connection."""
    
    disconnected_at: Optional[datetime] = Field(None, description="Disconnection timestamp")
    is_active: Optional[bool] = Field(None, description="Whether connection is active")
    ip_address: Optional[str] = Field(None, description="IP address (for WiFi connections)", pattern=r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    port: Optional[conint(gt=0, le=65535)] = Field(None, description="Port (for WiFi connections)")
    usb_serial: Optional[constr(min_length=1, max_length=255)] = Field(None, description="USB serial number (for USB connections)")
    user_id: Optional[uuid.UUID] = Field(None, description="ID of the authenticated user")
    connection_info: Optional[Dict[str, Any]] = Field(None, description="Additional connection information")
    notes: Optional[str] = Field(None, description="Additional notes")


class ConnectionResponse(BaseResponse):
    """Schema for connection response."""
    
    connection_type: str = Field(..., description="Connection type")
    connected_at: datetime = Field(..., description="Connection timestamp")
    disconnected_at: Optional[datetime] = Field(None, description="Disconnection timestamp")
    is_active: bool = Field(..., description="Whether connection is active")
    ip_address: Optional[str] = Field(None, description="IP address (for WiFi connections)")
    port: Optional[str] = Field(None, description="Port (for WiFi connections)")
    usb_serial: Optional[str] = Field(None, description="USB serial number (for USB connections)")
    device_id: uuid.UUID = Field(..., description="ID of the connected device")
    user_id: Optional[uuid.UUID] = Field(None, description="ID of the authenticated user")
    connection_info: Optional[Dict[str, Any]] = Field(None, description="Additional connection information")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")
    duration: Optional[conint(ge=-1)] = Field(None, description="Connection duration in seconds (-1 if still active)")


class ConnectionListResponse(BaseResponse):
    """Schema for connection list response with minimal fields."""
    
    connection_type: str = Field(..., description="Connection type")
    connected_at: datetime = Field(..., description="Connection timestamp")
    disconnected_at: Optional[datetime] = Field(None, description="Disconnection timestamp")
    is_active: bool = Field(..., description="Whether connection is active")
    device_id: uuid.UUID = Field(..., description="ID of the connected device")
    user_id: Optional[uuid.UUID] = Field(None, description="ID of the authenticated user")
    duration: Optional[conint(ge=-1)] = Field(None, description="Connection duration in seconds (-1 if still active)")


class ConnectionCloseRequest(BaseCreate):
    """Schema for closing a connection."""
    
    disconnected_at: Optional[datetime] = Field(None, description="Disconnection timestamp (defaults to current time if not provided)")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes about the disconnection")
