"""
HTTP Exception Factory for the NFC Reader/Writer System PC Server API.

This module provides a centralized factory for creating standardized HTTP exceptions
with consistent error message formatting and structure.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, status
from pydantic import ValidationError

# Set up logger
logger = logging.getLogger("nfc-server.api.exceptions")


class HTTPExceptionFactory:
    """Factory class for creating standardized HTTP exceptions."""
    
    @staticmethod
    def bad_request(
        detail: str,
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 400 Bad Request exception."""
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": detail,
                "code": code or "BAD_REQUEST",
                "params": params,
                "status_code": status.HTTP_400_BAD_REQUEST
            }
        )
    
    @staticmethod
    def unauthorized(
        detail: str = "Authentication required",
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 401 Unauthorized exception."""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "detail": detail,
                "code": code or "UNAUTHORIZED",
                "params": params,
                "status_code": status.HTTP_401_UNAUTHORIZED
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    def forbidden(
        detail: str = "Access forbidden",
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 403 Forbidden exception."""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": detail,
                "code": code or "FORBIDDEN",
                "params": params,
                "status_code": status.HTTP_403_FORBIDDEN
            }
        )
    
    @staticmethod
    def not_found(
        resource: str,
        identifier: Union[str, int] = None,
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 404 Not Found exception."""
        if identifier:
            detail = f"{resource} with identifier '{identifier}' not found"
        else:
            detail = f"{resource} not found"
            
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "detail": detail,
                "code": code or "NOT_FOUND",
                "params": params or {"resource": resource, "identifier": identifier},
                "status_code": status.HTTP_404_NOT_FOUND
            }
        )
    
    @staticmethod
    def conflict(
        detail: str,
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 409 Conflict exception."""
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": detail,
                "code": code or "CONFLICT",
                "params": params,
                "status_code": status.HTTP_409_CONFLICT
            }
        )
    
    @staticmethod
    def unprocessable_entity(
        detail: str,
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> HTTPException:
        """Create a 422 Unprocessable Entity exception."""
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": detail,
                "code": code or "UNPROCESSABLE_ENTITY",
                "params": params,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        )
    
    @staticmethod
    def internal_server_error(
        detail: str = "An internal server error occurred",
        code: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        log_exception: bool = True
    ) -> HTTPException:
        """Create a 500 Internal Server Error exception."""
        if log_exception:
            logger.exception("Internal server error occurred")
            
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "detail": detail,
                "code": code or "INTERNAL_SERVER_ERROR",
                "params": params,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        )
    
    @staticmethod
    def from_validation_error(
        validation_error: ValidationError,
        code: Optional[str] = None
    ) -> HTTPException:
        """Create a validation exception from Pydantic ValidationError."""
        errors = []
        for error in validation_error.errors():
            field_path = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "detail": "Validation failed",
                "code": code or "VALIDATION_ERROR",
                "errors": errors,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        )
    
    @staticmethod
    def duplicate_resource(
        resource: str,
        field: str,
        value: str,
        code: Optional[str] = None
    ) -> HTTPException:
        """Create a conflict exception for duplicate resources."""
        return HTTPExceptionFactory.conflict(
            detail=f"{resource} with {field} '{value}' already exists",
            code=code or "DUPLICATE_RESOURCE",
            params={
                "resource": resource,
                "field": field,
                "value": value
            }
        )
    
    @staticmethod
    def invalid_credentials(
        code: Optional[str] = None
    ) -> HTTPException:
        """Create an unauthorized exception for invalid credentials."""
        return HTTPExceptionFactory.unauthorized(
            detail="Invalid credentials provided",
            code=code or "INVALID_CREDENTIALS"
        )
    
    @staticmethod
    def account_locked(
        locked_until: Optional[str] = None,
        code: Optional[str] = None
    ) -> HTTPException:
        """Create a forbidden exception for locked accounts."""
        detail = "Account is locked"
        params = {}
        
        if locked_until:
            detail += f" until {locked_until}"
            params["locked_until"] = locked_until
            
        return HTTPExceptionFactory.forbidden(
            detail=detail,
            code=code or "ACCOUNT_LOCKED",
            params=params
        )
    
    @staticmethod
    def insufficient_permissions(
        required_permission: Optional[str] = None,
        code: Optional[str] = None
    ) -> HTTPException:
        """Create a forbidden exception for insufficient permissions."""
        detail = "Insufficient permissions"
        params = {}
        
        if required_permission:
            detail += f" (required: {required_permission})"
            params["required_permission"] = required_permission
            
        return HTTPExceptionFactory.forbidden(
            detail=detail,
            code=code or "INSUFFICIENT_PERMISSIONS",
            params=params
        )


class ValidationExceptionHandler:
    """Middleware-like handler for validation exceptions."""
    
    @staticmethod
    def handle_validation_error(validation_error: ValidationError) -> HTTPException:
        """Handle Pydantic ValidationError and return formatted HTTPException."""
        return HTTPExceptionFactory.from_validation_error(validation_error)
    
    @staticmethod
    def validate_and_raise(func):
        """Decorator to catch validation errors and convert them to HTTPExceptions."""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                raise ValidationExceptionHandler.handle_validation_error(e)
        return wrapper


# Common error codes for reference
class ErrorCodes:
    """Standard error codes used throughout the application."""
    
    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    FORBIDDEN = "FORBIDDEN"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Resources
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE_RESOURCE = "DUPLICATE_RESOURCE"
    CONFLICT = "CONFLICT"
    
    # System
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # Business Logic
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    RESOURCE_LIMIT_EXCEEDED = "RESOURCE_LIMIT_EXCEEDED"
    INVALID_STATE = "INVALID_STATE"
