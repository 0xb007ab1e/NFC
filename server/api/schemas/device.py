"""
Device API schemas for the NFC Reader/Writer System PC Server.

This module contains Pydantic models for Device API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from pydantic import Field, validator, constr, conint
from enum import Enum

from server.api.schemas.base import BaseResponse, BaseCreate, BaseUpdate


class ConnectionType(str, Enum):
    """Enum for connection types."""
    USB = "USB"
    WIFI = "WiFi"
    BLUETOOTH = "Bluetooth"
    UNKNOWN = "Unknown"


class DeviceCreate(BaseCreate):
    """Schema for creating a new device."""
    
    device_id: constr(min_length=1, max_length=255, pattern=r'^[a-zA-Z0-9_-]+$') = Field(..., description="Unique device identifier")
    name: constr(min_length=1, max_length=255) = Field(..., description="Device name")
    model: constr(min_length=1, max_length=255) = Field(..., description="Device model")
    manufacturer: constr(min_length=1, max_length=255) = Field(..., description="Device manufacturer")
    android_version: constr(min_length=1, max_length=50, pattern=r'^\d+(\.\d+)*') = Field(..., description="Android version")
    app_version: constr(min_length=1, max_length=50, pattern=r'^\d+(\.\d+)*') = Field(..., description="App version")
    supports_nfc: bool = Field(default=True, description="Whether device supports NFC")
    supports_ndef: bool = Field(default=True, description="Whether device supports NDEF")
    is_active: bool = Field(default=True, description="Whether device is active")
    last_connection_type: Optional[ConnectionType] = Field(None, description="Last connection type")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Additional device information")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")


class DeviceUpdate(BaseUpdate):
    """Schema for updating a device."""
    
    name: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Device name")
    model: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Device model")
    manufacturer: Optional[constr(min_length=1, max_length=255)] = Field(None, description="Device manufacturer")
    android_version: Optional[constr(min_length=1, max_length=50, pattern=r'^\d+(\.\d+)*')] = Field(None, description="Android version")
    app_version: Optional[constr(min_length=1, max_length=50, pattern=r'^\d+(\.\d+)*')] = Field(None, description="App version")
    supports_nfc: Optional[bool] = Field(None, description="Whether device supports NFC")
    supports_ndef: Optional[bool] = Field(None, description="Whether device supports NDEF")
    is_active: Optional[bool] = Field(None, description="Whether device is active")
    last_connection_type: Optional[ConnectionType] = Field(None, description="Last connection type")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Additional device information")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")


class DeviceResponse(BaseResponse):
    """Schema for device response."""
    
    device_id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Device name")
    model: str = Field(..., description="Device model")
    manufacturer: str = Field(..., description="Device manufacturer")
    android_version: str = Field(..., description="Android version")
    app_version: str = Field(..., description="App version")
    supports_nfc: bool = Field(..., description="Whether device supports NFC")
    supports_ndef: bool = Field(..., description="Whether device supports NDEF")
    is_active: bool = Field(..., description="Whether device is active")
    last_connection_type: Optional[str] = Field(None, description="Last connection type")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Additional device information")
    notes: Optional[str] = Field(None, description="Additional notes")


class DeviceListResponse(BaseResponse):
    """Schema for device list response with minimal fields."""
    
    device_id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Device name")
    model: str = Field(..., description="Device model")
    manufacturer: str = Field(..., description="Device manufacturer")
    is_active: bool = Field(..., description="Whether device is active")
    last_connection_type: Optional[str] = Field(None, description="Last connection type")
