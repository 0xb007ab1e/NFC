"""
Device API routes for the NFC Reader/Writer System PC Server.

This module contains the API endpoints for device management operations.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from server.db.config import get_db
from server.db.models.device import Device
from server.api.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceListResponse,
)

# Set up logger
logger = logging.getLogger("nfc-server.api.device")

# Create router
router = APIRouter()


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new device.
    
    This endpoint accepts device data and creates a new device record.
    """
    logger.info(f"Creating new device: {device_data.name}")
    
    # Check if device with the same device_id already exists
    existing_device = db.query(Device).filter(Device.device_id == device_data.device_id).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with ID {device_data.device_id} already exists"
        )
    
    try:
        # Create new device
        new_device = Device(
            device_id=device_data.device_id,
            name=device_data.name,
            model=device_data.model,
            manufacturer=device_data.manufacturer,
            android_version=device_data.android_version,
            app_version=device_data.app_version,
            supports_nfc=device_data.supports_nfc,
            supports_ndef=device_data.supports_ndef,
            is_active=device_data.is_active,
            last_connection_type=device_data.last_connection_type,
            device_info=device_data.device_info,
            notes=device_data.notes,
        )
        
        # Add to database
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        logger.info(f"Successfully created device with ID: {new_device.id}")
        return new_device
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating device: {str(e)}"
        )


@router.get("/", response_model=List[DeviceListResponse])
async def get_devices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: bool = Query(None, description="Filter by active status"),
    connection_type: str = Query(None, description="Filter by last connection type"),
    db: Session = Depends(get_db)
):
    """
    Get all devices.
    
    Returns a paginated list of all devices with optional filtering.
    """
    logger.info(f"Retrieving devices with skip={skip}, limit={limit}")
    
    query = db.query(Device)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Device.is_active == is_active)
    
    if connection_type:
        query = query.filter(Device.last_connection_type == connection_type)
    
    # Apply pagination
    devices = query.offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(devices)} devices")
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by ID.
    
    Returns the details of a specific device.
    """
    logger.info(f"Retrieving device with ID: {device_id}")
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    return device


@router.get("/by-device-id/{device_id}", response_model=DeviceResponse)
async def get_device_by_device_id(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific device by device ID.
    
    Returns the details of a specific device using the device_id field.
    """
    logger.info(f"Retrieving device with device_id: {device_id}")
    device = db.query(Device).filter(Device.device_id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with device_id {device_id} not found"
        )
    
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: UUID,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a device.
    
    Updates the details of a specific device.
    """
    logger.info(f"Updating device with ID: {device_id}")
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Update fields
    for key, value in device_data.dict(exclude_unset=True).items():
        setattr(device, key, value)
    
    try:
        db.commit()
        db.refresh(device)
        logger.info(f"Successfully updated device with ID: {device_id}")
        return device
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating device: {str(e)}"
        )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a device.
    
    Removes a device and all its associated records from the database.
    """
    logger.info(f"Deleting device with ID: {device_id}")
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    try:
        db.delete(device)
        db.commit()
        logger.info(f"Successfully deleted device with ID: {device_id}")
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting device: {str(e)}"
        )


@router.patch("/{device_id}/activate", response_model=DeviceResponse)
async def activate_device(
    device_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Activate a device.
    
    Sets the device status to active.
    """
    logger.info(f"Activating device with ID: {device_id}")
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    device.is_active = True
    
    try:
        db.commit()
        db.refresh(device)
        logger.info(f"Successfully activated device with ID: {device_id}")
        return device
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error activating device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activating device: {str(e)}"
        )


@router.patch("/{device_id}/deactivate", response_model=DeviceResponse)
async def deactivate_device(
    device_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deactivate a device.
    
    Sets the device status to inactive.
    """
    logger.info(f"Deactivating device with ID: {device_id}")
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    device.is_active = False
    
    try:
        db.commit()
        db.refresh(device)
        logger.info(f"Successfully deactivated device with ID: {device_id}")
        return device
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deactivating device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating device: {str(e)}"
        )
