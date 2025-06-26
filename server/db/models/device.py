"""
Device model for the NFC Reader/Writer System PC Server.

This module contains the Device model for storing connected Android device data.
"""

from typing import List
import uuid

from sqlalchemy import Column, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.db.models.base import BaseModel


class Device(BaseModel):
    """
    Device model.
    
    This model represents an Android device that connects to the server
    to send NFC tag data. It tracks device information and connection status.
    """

    # Device identification
    device_id = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    
    # Device specifications
    manufacturer = Column(String(255), nullable=False)
    android_version = Column(String(50), nullable=False)
    app_version = Column(String(50), nullable=False)
    
    # Device capabilities
    supports_nfc = Column(Boolean, default=True, nullable=False)
    supports_ndef = Column(Boolean, default=True, nullable=False)
    
    # Device status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    last_connection_type = Column(String(50), nullable=True)  # USB, WiFi, etc.
    
    # Additional information
    device_info = Column(JSON, nullable=True)  # Additional device information
    notes = Column(Text, nullable=True)
    
    # Relationships
    tags = relationship("NFCTag", back_populates="device")
    connections = relationship("Connection", back_populates="device")
    
    def __repr__(self) -> str:
        """
        String representation of the device.
        
        Returns:
            str: String representation.
        """
        return f"<Device(id={self.id}, name={self.name}, model={self.model})>"
