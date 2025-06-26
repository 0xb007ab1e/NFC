"""
User API schemas for the NFC Reader/Writer System PC Server.

This module contains Pydantic models for User API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from pydantic import Field, field_validator, constr, conint
from pydantic import EmailStr
from enum import Enum

from server.api.schemas.base import BaseResponse, BaseCreate, BaseUpdate


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserCreate(BaseCreate):
    """Schema for creating a new user."""
    
    username: constr(min_length=1, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$') = Field(..., description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: constr(min_length=8) = Field(..., description="User password")
    is_active: bool = Field(default=True, description="Whether user is active")
    is_admin: bool = Field(default=False, description="Whether user has admin privileges")
    permissions: Optional[List[constr(min_length=1, max_length=100)]] = Field(None, description="List of permissions")
    first_name: Optional[constr(min_length=1, max_length=50)] = Field(None, description="First name")
    last_name: Optional[constr(min_length=1, max_length=50)] = Field(None, description="Last name")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")

    @field_validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseUpdate):
    """Schema for updating a user."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    is_admin: Optional[bool] = Field(None, description="Whether user has admin privileges")
    permissions: Optional[List[str]] = Field(None, description="List of permissions")
    first_name: Optional[constr(min_length=1, max_length=50)] = Field(None, description="First name")
    last_name: Optional[constr(min_length=1, max_length=50)] = Field(None, description="Last name")
    notes: Optional[constr(max_length=1000)] = Field(None, description="Additional notes")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")


class UserPasswordUpdate(BaseUpdate):
    """Schema for updating user password."""
    
    current_password: constr(min_length=1) = Field(..., description="Current password")
    new_password: constr(min_length=8) = Field(..., description="New password")
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(BaseResponse):
    """Schema for user response."""
    
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user is active")
    is_admin: bool = Field(..., description="Whether user has admin privileges")
    permissions: Optional[List[str]] = Field(None, description="List of permissions")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    failed_login_attempts: conint(ge=0) = Field(..., description="Number of failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until timestamp")
    notes: Optional[str] = Field(None, description="Additional notes")
    user_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional user metadata")
    full_name: Optional[str] = Field(None, description="Full name")
    is_locked: bool = Field(..., description="Whether user account is locked")


class UserListResponse(BaseResponse):
    """Schema for user list response with minimal fields."""
    
    username: str = Field(..., description="Unique username")
    email: str = Field(..., description="User email address")
    is_active: bool = Field(..., description="Whether user is active")
    is_admin: bool = Field(..., description="Whether user has admin privileges")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    full_name: Optional[str] = Field(None, description="Full name")
    is_locked: bool = Field(..., description="Whether user account is locked")


class UserLoginRequest(BaseCreate):
    """Schema for user login request."""
    
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class UserLoginResponse(BaseCreate):
    """Schema for user login response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")
