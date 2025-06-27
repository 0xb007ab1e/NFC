"""
User API routes for the NFC Reader/Writer System PC Server.

This module contains the API endpoints for user management operations.
"""

import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from server.db.config import get_db
from server.db.models.user import User
from server.api.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserListResponse,
)
from server.api.exceptions import HTTPExceptionFactory, ErrorCodes

# Set up logger
logger = logging.getLogger("nfc-server.api.user")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create router
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    This endpoint accepts user data and creates a new user record.
    """
    logger.info(f"Creating new user: {user_data.username}")
    
    # Check if user with the same username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPExceptionFactory.duplicate_resource(
            resource="User",
            field="username",
            value=user_data.username,
            code=ErrorCodes.DUPLICATE_RESOURCE
        )
    
    # Check if user with the same email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPExceptionFactory.duplicate_resource(
            resource="User",
            field="email",
            value=user_data.email,
            code=ErrorCodes.DUPLICATE_RESOURCE
        )
    
    try:
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin,
            permissions=user_data.permissions,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            notes=user_data.notes,
            user_metadata=user_data.user_metadata,
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Successfully created user with ID: {new_user.id}")
        return new_user
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error creating user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.get("/", response_model=List[UserListResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: bool = Query(None, description="Filter by active status"),
    is_admin: bool = Query(None, description="Filter by admin status"),
    db: Session = Depends(get_db)
):
    """
    Get all users.
    
    Returns a paginated list of all users with optional filtering.
    """
    logger.info(f"Retrieving users with skip={skip}, limit={limit}")
    
    query = db.query(User)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    # Apply pagination and ordering (by username)
    users = query.order_by(User.username).offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(users)} users")
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    
    Returns the details of a specific user.
    """
    logger.info(f"Retrieving user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    return user


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by username.
    
    Returns the details of a specific user using the username field.
    """
    logger.info(f"Retrieving user with username: {username}")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=username,
            code=ErrorCodes.NOT_FOUND
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a user.
    
    Updates the details of a specific user.
    """
    logger.info(f"Updating user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    # Check if email already exists (if being updated)
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPExceptionFactory.duplicate_resource(
                resource="User",
                field="email",
                value=user_data.email,
                code=ErrorCodes.DUPLICATE_RESOURCE
            )
    
    # Update fields
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Successfully updated user with ID: {user_id}")
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error updating user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.patch("/{user_id}/password", response_model=UserResponse)
async def update_user_password(
    user_id: UUID,
    password_data: UserPasswordUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a user's password.
    
    Updates the password of a specific user after verifying the current password.
    """
    logger.info(f"Updating password for user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise HTTPExceptionFactory.bad_request(
            detail="Current password is incorrect",
            code=ErrorCodes.INVALID_CREDENTIALS
        )
    
    # Hash new password
    new_password_hash = get_password_hash(password_data.new_password)
    user.password_hash = new_password_hash
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Successfully updated password for user with ID: {user_id}")
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating password: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error updating password: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    
    Removes a user and all associated records from the database.
    """
    logger.info(f"Deleting user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    try:
        db.delete(user)
        db.commit()
        logger.info(f"Successfully deleted user with ID: {user_id}")
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error deleting user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Activate a user.
    
    Sets the user status to active and clears any account locks.
    """
    logger.info(f"Activating user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    user.is_active = True
    user.failed_login_attempts = 0
    user.locked_until = None
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Successfully activated user with ID: {user_id}")
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error activating user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deactivate a user.
    
    Sets the user status to inactive.
    """
    logger.info(f"Deactivating user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    user.is_active = False
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Successfully deactivated user with ID: {user_id}")
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error deactivating user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )


@router.patch("/{user_id}/unlock", response_model=UserResponse)
async def unlock_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Unlock a user account.
    
    Clears account locks and resets failed login attempts.
    """
    logger.info(f"Unlocking user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPExceptionFactory.not_found(
            resource="User",
            identifier=str(user_id),
            code=ErrorCodes.NOT_FOUND
        )
    
    user.failed_login_attempts = 0
    user.locked_until = None
    
    try:
        db.commit()
        db.refresh(user)
        logger.info(f"Successfully unlocked user with ID: {user_id}")
        return user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error unlocking user: {str(e)}")
        raise HTTPExceptionFactory.internal_server_error(
            detail=f"Error unlocking user: {str(e)}",
            code=ErrorCodes.DATABASE_ERROR
        )
