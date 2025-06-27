"""
Connection model for the NFC Reader/Writer System PC Server.

This module contains the Connection model for tracking device connections.
"""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.db.models.base import BaseModel


class Connection(BaseModel):
    """
    Connection model.
    
    This model tracks connections from Android devices to the server.
    It records connection type, duration, and status.
    """

    # Connection identification
    connection_type = Column(String(50), nullable=False, index=True)  # USB, WiFi
    
    # Connection timing
    connected_at = Column(DateTime, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    
    # Connection status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Connection details
    ip_address = Column(String(50), nullable=True)  # For WiFi connections
    port = Column(String(10), nullable=True)  # For WiFi connections
    usb_serial = Column(String(255), nullable=True)  # For USB connections
    
    # Device relationship
    device_id = Column(UUID(as_uuid=True), ForeignKey("device.id"), nullable=False)
    device = relationship("Device", back_populates="connections")
    
    # User relationship (if authenticated)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="connections")
    
    # Additional data
    connection_info = Column(JSON, nullable=True)  # Additional connection info
    notes = Column(Text, nullable=True)
    
    def __repr__(self) -> str:
        """
        String representation of the connection.
        
        Returns:
            str: String representation.
        """
        return f"<Connection(id={self.id}, type={self.connection_type}, active={self.is_active})>"
        
    @property
    def duration(self) -> int:
        """
        Get the connection duration in seconds.
        
        Returns:
            int: Duration in seconds or -1 if still active.
        """
        if not self.disconnected_at:
            return -1
            
        duration = self.disconnected_at - self.connected_at
        return int(duration.total_seconds())
