"""
NFC schemas for the NFC Reader/Writer System PC Server API.

This module contains Pydantic models for NFC tag and record data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import Field, field_validator, constr, conint
from enum import Enum

from server.api.schemas.base import BaseCreate, BaseResponse, BaseUpdate


class TNFType(int, Enum):
    """Enum for TNF (Type Name Format) values."""
    EMPTY = 0
    WELL_KNOWN = 1
    MEDIA = 2
    ABSOLUTE_URI = 3
    EXTERNAL = 4
    UNKNOWN = 5
    UNCHANGED = 6
    

class NFCTagType(str, Enum):
    """Enum for NFC tag types."""
    TYPE1 = "Type1"
    TYPE2 = "Type2"
    TYPE3 = "Type3"
    TYPE4 = "Type4"
    UNKNOWN = "Unknown"


class NFCRecordCreate(BaseCreate):
    """Schema for creating an NFC record."""
    
    tnf: TNFType = Field(..., description="Type Name Format")
    type: str = Field(..., description="Record type", max_length=255)
    payload: Optional[bytes] = Field(None, description="Binary payload data")
    payload_str: Optional[str] = Field(None, description="String representation of payload", max_length=10000)
    record_index: conint(ge=0) = Field(..., description="Position in the tag")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed data in JSON format")
    tag_id: Optional[uuid.UUID] = Field(None, description="Tag ID (optional when creating with tag)")


class NFCRecordResponse(BaseResponse):
    """Schema for NFC record response."""
    
    tnf: int
    type: str
    payload: Optional[bytes] = None
    payload_str: Optional[str] = None
    tag_id: uuid.UUID
    record_index: int
    parsed_data: Optional[Dict[str, Any]] = None
    
    # Computed properties
    mime_type: Optional[str] = None
    uri: Optional[str] = None
    text: Optional[str] = None


class NFCTagCreate(BaseCreate):
    """Schema for creating an NFC tag."""
    
    uid: str = Field(..., description="Unique identifier of the tag (hex format)", min_length=8, max_length=128, pattern=r'^[0-9A-Fa-f]+$')
    tech_list: List[str] = Field(..., description="List of technologies supported by the tag")
    tag_type: NFCTagType = Field(..., description="Type of the tag")
    is_writable: bool = Field(False, description="Whether the tag is writable")
    is_ndef_formatted: bool = Field(False, description="Whether the tag is NDEF formatted")
    max_size: Optional[conint(gt=0)] = Field(None, description="Maximum size of the tag in bytes")
    read_timestamp: datetime = Field(..., description="Timestamp when the tag was read")
    read_location: Optional[Dict[str, float]] = Field(
        None, 
        description="GPS coordinates where the tag was read"
    )
    device_id: uuid.UUID = Field(..., description="ID of the device that read the tag")
    notes: Optional[str] = Field(None, description="Additional notes about the tag", max_length=1000)
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom data associated with the tag")
    
    # Records to create with the tag
    records: List[NFCRecordCreate] = Field([], description="Records contained in the tag")
    
    @field_validator('tech_list')
    def validate_tech_list(cls, v):
        if len(v) == 0:
            raise ValueError('tech_list cannot be empty')
        return v


class NFCTagResponse(BaseResponse):
    """Schema for NFC tag response."""
    
    uid: str
    tech_list: List[str]
    tag_type: str
    is_writable: bool
    is_ndef_formatted: bool
    max_size: Optional[int] = None
    read_timestamp: datetime
    read_location: Optional[Dict[str, float]] = None
    device_id: uuid.UUID
    notes: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None
    
    # Related records
    records: List[NFCRecordResponse] = []


class NFCTagUpdate(BaseUpdate):
    """Schema for updating an NFC tag."""
    
    is_writable: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)
    custom_data: Optional[Dict[str, Any]] = None
