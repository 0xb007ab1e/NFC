"""
Custom validation utilities for the NFC Reader/Writer System PC Server API.

This module provides custom validators, field constraints, and validation helpers
to be used across different Pydantic schemas.
"""

import re
from typing import Any, Dict, List, Optional, Union
from pydantic import validator, Field, constr, conint
from enum import Enum


class ValidationRegex:
    """Collection of commonly used regex patterns for validation."""
    
    # Network related
    IPV4_PATTERN = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    MAC_ADDRESS_PATTERN = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    
    # Identifiers
    USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'
    DEVICE_ID_PATTERN = r'^[a-zA-Z0-9_-]+$'
    HEX_PATTERN = r'^[0-9A-Fa-f]+$'
    
    # Version patterns
    VERSION_PATTERN = r'^\d+(\.\d+)*(-[a-zA-Z0-9]+)*$'
    SEMANTIC_VERSION_PATTERN = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)*$'
    
    # NFC specific
    NFC_UID_PATTERN = r'^[0-9A-Fa-f]{8,32}$'  # 4-16 bytes in hex
    NDEF_TYPE_PATTERN = r'^[a-zA-Z0-9._-]+$'


class CommonConstraints:
    """Collection of commonly used Pydantic field constraints."""
    
    # String constraints
    Username = constr(min_length=1, max_length=50, pattern=ValidationRegex.USERNAME_PATTERN)
    DeviceId = constr(min_length=1, max_length=255, pattern=ValidationRegex.DEVICE_ID_PATTERN)
    ShortText = constr(min_length=1, max_length=255)
    MediumText = constr(min_length=1, max_length=1000)
    LongText = constr(max_length=10000)
    Notes = constr(max_length=1000)
    
    # Network constraints
    IPAddress = constr(pattern=ValidationRegex.IPV4_PATTERN)
    MacAddress = constr(pattern=ValidationRegex.MAC_ADDRESS_PATTERN)
    
    # Version constraints
    Version = constr(min_length=1, max_length=50, pattern=ValidationRegex.VERSION_PATTERN)
    SemanticVersion = constr(min_length=5, max_length=50, pattern=ValidationRegex.SEMANTIC_VERSION_PATTERN)
    
    # Integer constraints
    Port = conint(gt=0, le=65535)
    PositiveInt = conint(gt=0)
    NonNegativeInt = conint(ge=0)
    
    # NFC specific constraints
    NFCUid = constr(min_length=8, max_length=32, pattern=ValidationRegex.NFC_UID_PATTERN)
    NDEFType = constr(min_length=1, max_length=255, pattern=ValidationRegex.NDEF_TYPE_PATTERN)


class ValidationHelpers:
    """Collection of validation helper functions."""
    
    @staticmethod
    def validate_password_strength(password: str) -> str:
        """
        Validate password strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            The validated password
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', password):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError('Password must contain at least one special character')
        
        return password
    
    @staticmethod
    def validate_email_domain(email: str, allowed_domains: Optional[List[str]] = None) -> str:
        """
        Validate email domain against allowed list.
        
        Args:
            email: Email address to validate
            allowed_domains: Optional list of allowed domains
            
        Returns:
            The validated email
            
        Raises:
            ValueError: If domain is not allowed
        """
        if allowed_domains:
            domain = email.split('@')[1].lower()
            if domain not in [d.lower() for d in allowed_domains]:
                raise ValueError(f'Email domain must be one of: {", ".join(allowed_domains)}')
        
        return email
    
    @staticmethod
    def validate_hex_string(value: str, min_length: int = 1, max_length: int = 255) -> str:
        """
        Validate hexadecimal string.
        
        Args:
            value: Hex string to validate
            min_length: Minimum length
            max_length: Maximum length
            
        Returns:
            The validated hex string (uppercase)
            
        Raises:
            ValueError: If not valid hex or wrong length
        """
        if not re.match(ValidationRegex.HEX_PATTERN, value):
            raise ValueError('Value must be a valid hexadecimal string')
        
        if not (min_length <= len(value) <= max_length):
            raise ValueError(f'Hex string length must be between {min_length} and {max_length} characters')
        
        return value.upper()
    
    @staticmethod
    def validate_nfc_uid(uid: str) -> str:
        """
        Validate NFC UID format.
        
        Args:
            uid: NFC UID to validate
            
        Returns:
            The validated UID (uppercase)
            
        Raises:
            ValueError: If UID format is invalid
        """
        # Remove any separators
        clean_uid = uid.replace(':', '').replace('-', '').replace(' ', '')
        
        # Validate hex format and length (4-16 bytes = 8-32 hex chars)
        if not re.match(r'^[0-9A-Fa-f]{8,32}$', clean_uid):
            raise ValueError('NFC UID must be 4-16 bytes in hexadecimal format')
        
        # Ensure even length (each byte = 2 hex chars)
        if len(clean_uid) % 2 != 0:
            raise ValueError('NFC UID must have even number of hex characters')
        
        return clean_uid.upper()
    
    @staticmethod
    def validate_file_size(size: int, max_size_mb: int = 10) -> int:
        """
        Validate file size.
        
        Args:
            size: File size in bytes
            max_size_mb: Maximum allowed size in MB
            
        Returns:
            The validated size
            
        Raises:
            ValueError: If size exceeds limit
        """
        max_bytes = max_size_mb * 1024 * 1024
        if size > max_bytes:
            raise ValueError(f'File size cannot exceed {max_size_mb}MB')
        
        return size
    
    @staticmethod
    def validate_json_field(value: Any, max_depth: int = 5) -> Any:
        """
        Validate JSON field depth and content.
        
        Args:
            value: JSON value to validate
            max_depth: Maximum nesting depth allowed
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If JSON is too deeply nested
        """
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValueError(f'JSON nesting depth cannot exceed {max_depth} levels')
            
            if isinstance(obj, dict):
                for v in obj.values():
                    check_depth(v, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        if value is not None:
            check_depth(value)
        
        return value


class CustomValidators:
    """Collection of custom validator decorators."""
    
    @staticmethod
    def password_strength_validator(field_name: str = 'password'):
        """Decorator for password strength validation."""
        def decorator(cls):
            @validator(field_name)
            def validate_password(cls, v):
                return ValidationHelpers.validate_password_strength(v)
            
            setattr(cls, f'validate_{field_name}', validate_password)
            return cls
        return decorator
    
    @staticmethod
    def conditional_required_validator(field_name: str, condition_field: str, condition_value: Any):
        """Decorator for conditional field requirement validation."""
        def decorator(cls):
            @validator(field_name)
            def validate_conditional(cls, v, values):
                if values.get(condition_field) == condition_value and not v:
                    raise ValueError(f'{field_name} is required when {condition_field} is {condition_value}')
                return v
            
            setattr(cls, f'validate_{field_name}_conditional', validate_conditional)
            return cls
        return decorator
    
    @staticmethod
    def unique_list_validator(field_name: str):
        """Decorator for ensuring list values are unique."""
        def decorator(cls):
            @validator(field_name)
            def validate_unique_list(cls, v):
                if v and len(v) != len(set(v)):
                    raise ValueError(f'{field_name} must contain unique values')
                return v
            
            setattr(cls, f'validate_{field_name}_unique', validate_unique_list)
            return cls
        return decorator


# Common field definitions that can be imported
class CommonFields:
    """Pre-configured field definitions for common use cases."""
    
    username = Field(..., description="Unique username", example="john_doe")
    email = Field(..., description="Email address", example="john@example.com")
    password = Field(..., description="Password (minimum 8 characters)", example="SecurePass123!")
    device_id = Field(..., description="Unique device identifier", example="device_001")
    notes = Field(None, description="Additional notes", example="Important device")
    
    # Network fields
    ip_address = Field(None, description="IP address", example="192.168.1.100")
    port = Field(None, description="Port number", example=8080)
    mac_address = Field(None, description="MAC address", example="00:11:22:33:44:55")
    
    # NFC fields
    nfc_uid = Field(..., description="NFC tag UID in hex format", example="04A1B2C3")
    tnf = Field(..., description="Type Name Format (0-6)", example=1)
    payload_size = Field(None, description="Payload size in bytes", example=256)
    
    # Pagination fields
    skip = Field(0, ge=0, description="Number of records to skip", example=0)
    limit = Field(100, ge=1, le=1000, description="Maximum number of records to return", example=100)
