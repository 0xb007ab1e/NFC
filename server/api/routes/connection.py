"""
Connection API routes for the NFC Reader/Writer System PC Server.

This module contains the API endpoints for connection management operations.
"""

import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.db.config import get_db
from server.db.models.connection import Connection
from server.db.models.device import Device
from server.db.models.user import User
from server.api.schemas.connection import (
    ConnectionCreate,
    ConnectionUpdate,
    ConnectionResponse,
    ConnectionListResponse,
    ConnectionCloseRequest,
)

# Set up logger
logger = logging.getLogger("nfc-server.api.connection")

# Create router
router = APIRouter()


@router.post("/", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new connection.
    
    This endpoint accepts connection data and creates a new connection record.
    """
    logger.info(f"Creating new connection for device: {connection_data.device_id}")
    
    # Check if device exists
    device = db.query(Device).filter(Device.id == connection_data.device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {connection_data.device_id} not found"
        )
    
    # Check if user exists (if provided)
    if connection_data.user_id:
        user = db.query(User).filter(User.id == connection_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {connection_data.user_id} not found"
            )
    
    try:
        # Create new connection
        new_connection = Connection(
            connection_type=connection_data.connection_type,
            connected_at=connection_data.connected_at,
            is_active=connection_data.is_active,
            ip_address=connection_data.ip_address,
            port=connection_data.port,
            usb_serial=connection_data.usb_serial,
            device_id=connection_data.device_id,
            user_id=connection_data.user_id,
            connection_info=connection_data.connection_info,
            notes=connection_data.notes,
        )
        
        # Add to database
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        
        # Update device's last connection type
        device.last_connection_type = connection_data.connection_type
        db.commit()
        
        logger.info(f"Successfully created connection with ID: {new_connection.id}")
        return new_connection
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating connection: {str(e)}"
        )


@router.get("/", response_model=List[ConnectionListResponse])
async def get_connections(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: bool = Query(None, description="Filter by active status"),
    connection_type: str = Query(None, description="Filter by connection type"),
    device_id: UUID = Query(None, description="Filter by device ID"),
    user_id: UUID = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """
    Get all connections.
    
    Returns a paginated list of all connections with optional filtering.
    """
    logger.info(f"Retrieving connections with skip={skip}, limit={limit}")
    
    query = db.query(Connection)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Connection.is_active == is_active)
    
    if connection_type:
        query = query.filter(Connection.connection_type == connection_type)
    
    if device_id:
        query = query.filter(Connection.device_id == device_id)
    
    if user_id:
        query = query.filter(Connection.user_id == user_id)
    
    # Apply pagination and ordering (most recent first)
    connections = query.order_by(Connection.connected_at.desc()).offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(connections)} connections")
    return connections


@router.get("/{connection_id}", response_model=ConnectionResponse)
async def get_connection(
    connection_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific connection by ID.
    
    Returns the details of a specific connection.
    """
    logger.info(f"Retrieving connection with ID: {connection_id}")
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found"
        )
    
    return connection


@router.get("/device/{device_id}", response_model=List[ConnectionListResponse])
async def get_device_connections(
    device_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all connections for a specific device.
    
    Returns a list of all connections associated with the specified device.
    """
    logger.info(f"Retrieving connections for device with ID: {device_id}")
    
    # Check if device exists
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    query = db.query(Connection).filter(Connection.device_id == device_id)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Connection.is_active == is_active)
    
    # Apply pagination and ordering (most recent first)
    connections = query.order_by(Connection.connected_at.desc()).offset(skip).limit(limit).all()
    
    return connections


@router.put("/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: UUID,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a connection.
    
    Updates the details of a specific connection.
    """
    logger.info(f"Updating connection with ID: {connection_id}")
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found"
        )
    
    # Check if user exists (if provided)
    if connection_data.user_id:
        user = db.query(User).filter(User.id == connection_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {connection_data.user_id} not found"
            )
    
    # Update fields
    for key, value in connection_data.model_dump(exclude_unset=True).items():
        setattr(connection, key, value)
    
    try:
        db.commit()
        db.refresh(connection)
        logger.info(f"Successfully updated connection with ID: {connection_id}")
        return connection
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating connection: {str(e)}"
        )


@router.patch("/{connection_id}/close", response_model=ConnectionResponse)
async def close_connection(
    connection_id: UUID,
    close_data: ConnectionCloseRequest = None,
    db: Session = Depends(get_db)
):
    """
    Close a connection.
    
    Sets the connection as inactive and records the disconnection time.
    """
    logger.info(f"Closing connection with ID: {connection_id}")
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found"
        )
    
    if not connection.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection with ID {connection_id} is already closed"
        )
    
    # Set connection as inactive and record disconnection time
    connection.is_active = False
    connection.disconnected_at = close_data.disconnected_at if close_data else datetime.utcnow()
    
    if close_data and close_data.notes:
        connection.notes = close_data.notes
    
    try:
        db.commit()
        db.refresh(connection)
        logger.info(f"Successfully closed connection with ID: {connection_id}")
        return connection
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error closing connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error closing connection: {str(e)}"
        )


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a connection.
    
    Removes a connection record from the database.
    """
    logger.info(f"Deleting connection with ID: {connection_id}")
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection with ID {connection_id} not found"
        )
    
    try:
        db.delete(connection)
        db.commit()
        logger.info(f"Successfully deleted connection with ID: {connection_id}")
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting connection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting connection: {str(e)}"
        )


@router.get("/active/", response_model=List[ConnectionListResponse])
async def get_active_connections(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    connection_type: str = Query(None, description="Filter by connection type"),
    db: Session = Depends(get_db)
):
    """
    Get all active connections.
    
    Returns a list of all currently active connections.
    """
    logger.info("Retrieving active connections")
    
    query = db.query(Connection).filter(Connection.is_active == True)
    
    # Apply filters
    if connection_type:
        query = query.filter(Connection.connection_type == connection_type)
    
    # Apply pagination and ordering (most recent first)
    connections = query.order_by(Connection.connected_at.desc()).offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(connections)} active connections")
    return connections
