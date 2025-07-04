"""
NFC schemas for the NFC Reader/Writer System PC Server API.

This module contains Pydantic models for NFC tag and record data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import Field

from server.api.schemas.base import BaseCreate, BaseResponse


class NFCRecordCreate(BaseCreate):
    """Schema for creating an NFC record."""
    
    tnf: int = Field(..., description="Type Name Format")
    type: str = Field(..., description="Record type")
    payload: Optional[bytes] = Field(None, description="Binary payload data")
    payload_str: Optional[str] = Field(None, description="String representation of payload")
    record_index: int = Field(..., description="Position in the tag")
    parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed data in JSON format")


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
    
    uid: str = Field(..., description="Unique identifier of the tag")
    tech_list: List[str] = Field(..., description="List of technologies supported by the tag")
    tag_type: str = Field(..., description="Type of the tag")
    is_writable: bool = Field(False, description="Whether the tag is writable")
    is_ndef_formatted: bool = Field(False, description="Whether the tag is NDEF formatted")
    max_size: Optional[int] = Field(None, description="Maximum size of the tag in bytes")
    read_timestamp: datetime = Field(..., description="Timestamp when the tag was read")
    read_location: Optional[Dict[str, float]] = Field(
        None, 
        description="GPS coordinates where the tag was read"
    )
    device_id: uuid.UUID = Field(..., description="ID of the device that read the tag")
    notes: Optional[str] = Field(None, description="Additional notes about the tag")
    custom_data: Optional[Dict[str, Any]] = Field(None, description="Custom data associated with the tag")
    
    # Records to create with the tag
    records: List[NFCRecordCreate] = Field([], description="Records contained in the tag")


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
