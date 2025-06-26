"""
NFC Tag model for the NFC Reader/Writer System PC Server.

This module contains the NFCTag model for storing NFC tag data.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from server.db.models.base import BaseModel


class NFCTag(BaseModel):
    """
    NFC Tag model.
    
    This model represents an NFC tag scanned by the Android application.
    It contains metadata about the tag and has a relationship to NFCRecord
    instances containing the actual data.
    """
    
    __tablename__ = "nfc_tag"

    # Tag identification
    uid = Column(String(255), index=True, nullable=False)
    tech_list = Column(JSONB, nullable=False)  # JSON array of technologies
    
    # Tag type information
    tag_type = Column(String(50), nullable=False, index=True)
    is_writable = Column(Boolean, default=False, nullable=False)
    is_ndef_formatted = Column(Boolean, default=False, nullable=False)
    max_size = Column(Integer, nullable=True)
    
    # Read information
    read_timestamp = Column(DateTime, nullable=False)
    read_location = Column(JSONB, nullable=True)  # Optional GPS coordinates
    
    # Device relationship
    device_id = Column(UUID(as_uuid=True), ForeignKey("device.id"), nullable=False)
    device = relationship("Device", back_populates="tags")
    
    # Records relationship
    records = relationship("NFCRecord", back_populates="tag", cascade="all, delete-orphan")
    
    # Additional data
    notes = Column(Text, nullable=True)
    custom_data = Column(JSONB, nullable=True)  # Any additional custom data
    
    def __repr__(self) -> str:
        """
        String representation of the NFC tag.
        
        Returns:
            str: String representation.
        """
        return f"<NFCTag(id={self.id}, uid={self.uid}, tag_type={self.tag_type})>"
