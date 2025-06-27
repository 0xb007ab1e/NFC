"""
Base model for the NFC Reader/Writer System PC Server.

This module contains the base model class for all database models.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

from server.db.config import Base


class BaseModel(Base):
    """Base model class for all database models."""

    __abstract__ = True

    # Primary key column using UUID
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    # Timestamp columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate table name automatically from class name.
        
        Returns:
            str: Table name in snake_case.
        """
        # Convert CamelCase to snake_case
        name = cls.__name__
        return "".join(
            ["_" + c.lower() if c.isupper() else c for c in name]
        ).lstrip("_")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Convert UUID to string
            if isinstance(value, uuid.UUID):
                value = str(value)
                
            # Convert datetime to ISO format
            elif isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
        return result
