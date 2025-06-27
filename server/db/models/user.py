"""
User model for the NFC Reader/Writer System PC Server.

This module contains the User model for storing user authentication data.
"""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, func, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from server.db.models.base import BaseModel


class User(BaseModel):
    """
    User model.
    
    This model represents a user who can authenticate with the system.
    It stores authentication data and permissions.
    """

    # User identification
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Authorization
    is_admin = Column(Boolean, default=False, nullable=False)
    permissions = Column(JSON, nullable=True)  # JSON array of permissions
    
    # User information
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    
    # Account management
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    user_metadata = Column(JSONB, nullable=True)  # Additional user metadata
    
    # Relationships
    connections = relationship("Connection", back_populates="user")
    
    def __repr__(self) -> str:
        """
        String representation of the user.
        
        Returns:
            str: String representation.
        """
        return f"<User(id={self.id}, username={self.username})>"
        
    @property
    def full_name(self) -> str:
        """
        Get the user's full name.
        
        Returns:
            str: Full name or username if not available.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
        
    @property
    def is_locked(self) -> bool:
        """
        Check if the user account is locked.
        
        Returns:
            bool: True if locked, False otherwise.
        """
        if not self.locked_until:
            return False
            
        return self.locked_until > datetime.utcnow()
