"""
Base schema for the NFC Reader/Writer System PC Server API.

This module contains the base Pydantic models for API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
import uuid

from pydantic import BaseModel, Field, ConfigDict


class APIModel(BaseModel):
    """Base model for all API schemas."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model -> Pydantic model conversion
        populate_by_name=True,  # Allow both alias and original name
        validate_assignment=True,  # Validate attribute assignments
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            uuid.UUID: lambda id: str(id),
        },
    )


class BaseResponse(APIModel):
    """Base response model with ID and timestamps."""
    
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BaseCreate(APIModel):
    """Base create model."""
    pass


class BaseUpdate(APIModel):
    """Base update model."""
    pass


class PaginatedResponse(APIModel):
    """Paginated response model."""
    
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total: int,
        page: int,
        size: int,
    ) -> "PaginatedResponse":
        """Create a paginated response."""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
        )


class ErrorResponse(APIModel):
    """Error response model."""
    
    detail: str
    code: str
    status_code: int
    params: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None  # For validation errors
