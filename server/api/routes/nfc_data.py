"""
NFC Data API routes for the NFC Reader/Writer System PC Server.

This module defines the API endpoints for NFC data operations.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server.api.schemas.nfc import (
    NFCTagCreate,
    NFCTagResponse,
    NFCTagUpdate,
    NFCRecordCreate,
    NFCRecordResponse
)
from server.db.config import get_db
from server.db.models import NFCTag, NFCRecord

# Set up logger
logger = logging.getLogger("nfc-server.api.routes.nfc_data")

# Create router
router = APIRouter()


@router.post("/tags", response_model=NFCTagResponse, status_code=status.HTTP_201_CREATED)
async def create_nfc_tag(
    tag_data: NFCTagCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new NFC tag record.
    
    This endpoint accepts NFC tag data from a mobile device and stores it in the database.
    """
    logger.info(f"Creating new NFC tag: {tag_data.uid}")
    
    # Check if tag already exists
    existing_tag = db.query(NFCTag).filter(NFCTag.uid == tag_data.uid).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"NFC tag with UID {tag_data.uid} already exists"
        )
    
    # Create new tag
    try:
        # Convert from schema to model
        new_tag = NFCTag(
            uid=tag_data.uid,
            tech_list=tag_data.tech_list,
            tag_type=tag_data.tag_type.value,
            is_writable=tag_data.is_writable,
            is_ndef_formatted=tag_data.is_ndef_formatted,
            max_size=tag_data.max_size,
            read_timestamp=tag_data.read_timestamp,
            read_location=tag_data.read_location,
            device_id=tag_data.device_id,
            notes=tag_data.notes,
            custom_data=tag_data.custom_data
        )
        
        # Add to database
        db.add(new_tag)
        db.flush()  # Get the tag ID before creating records
        
        # Create associated records
        for record_data in tag_data.records:
            new_record = NFCRecord(
                tnf=record_data.tnf,
                type=record_data.type,
                payload=record_data.payload,
                payload_str=record_data.payload_str,
                tag_id=new_tag.id,
                record_index=record_data.record_index,
                parsed_data=record_data.parsed_data
            )
            db.add(new_record)
        
        db.commit()
        db.refresh(new_tag)
        
        logger.info(f"Successfully created NFC tag with ID: {new_tag.id} and {len(tag_data.records)} records")
        return new_tag
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating NFC tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating NFC tag: {str(e)}"
        )


@router.get("/tags", response_model=List[NFCTagResponse])
async def get_nfc_tags(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get a list of NFC tags.
    
    Returns a paginated list of NFC tags stored in the database.
    """
    logger.info(f"Retrieving NFC tags (skip={skip}, limit={limit})")
    tags = db.query(NFCTag).offset(skip).limit(limit).all()
    return tags


@router.get("/tags/{tag_id}", response_model=NFCTagResponse)
async def get_nfc_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific NFC tag by ID.
    
    Returns the details of a specific NFC tag.
    """
    logger.info(f"Retrieving NFC tag with ID: {tag_id}")
    tag = db.query(NFCTag).filter(NFCTag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC tag with ID {tag_id} not found"
        )
    
    return tag


@router.put("/tags/{tag_id}", response_model=NFCTagResponse)
async def update_nfc_tag(
    tag_id: UUID,
    tag_data: NFCTagUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing NFC tag.
    
    Updates the details of a specific NFC tag.
    """
    logger.info(f"Updating NFC tag with ID: {tag_id}")
    tag = db.query(NFCTag).filter(NFCTag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC tag with ID {tag_id} not found"
        )
    
    # Update fields
    for key, value in tag_data.model_dump(exclude_unset=True).items():
        setattr(tag, key, value)
    
    try:
        db.commit()
        db.refresh(tag)
        logger.info(f"Successfully updated NFC tag with ID: {tag_id}")
        return tag
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating NFC tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating NFC tag: {str(e)}"
        )


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nfc_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an NFC tag.
    
    Removes an NFC tag and all its associated records from the database.
    """
    logger.info(f"Deleting NFC tag with ID: {tag_id}")
    tag = db.query(NFCTag).filter(NFCTag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC tag with ID {tag_id} not found"
        )
    
    try:
        db.delete(tag)
        db.commit()
        logger.info(f"Successfully deleted NFC tag with ID: {tag_id}")
        return None
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting NFC tag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting NFC tag: {str(e)}"
        )


@router.post("/records", response_model=NFCRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_nfc_record(
    record_data: NFCRecordCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new NFC record.
    
    This endpoint accepts NFC record data and associates it with an existing tag.
    """
    logger.info(f"Creating new NFC record for tag: {record_data.tag_id}")
    
    # Check if tag exists
    tag = db.query(NFCTag).filter(NFCTag.id == record_data.tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC tag with ID {record_data.tag_id} not found"
        )
    
    # Create new record
    try:
        # Convert from schema to model
        new_record = NFCRecord(
            tnf=record_data.tnf,
            type=record_data.type,
            payload=record_data.payload,
            payload_str=record_data.payload_str,
            tag_id=record_data.tag_id,
            record_index=record_data.record_index,
            parsed_data=record_data.parsed_data
        )
        
        # Add to database
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        logger.info(f"Successfully created NFC record with ID: {new_record.id}")
        return new_record
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating NFC record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating NFC record: {str(e)}"
        )


@router.get("/records/{record_id}", response_model=NFCRecordResponse)
async def get_nfc_record(
    record_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific NFC record by ID.
    
    Returns the details of a specific NFC record.
    """
    logger.info(f"Retrieving NFC record with ID: {record_id}")
    record = db.query(NFCRecord).filter(NFCRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC record with ID {record_id} not found"
        )
    
    return record


@router.get("/tags/{tag_id}/records", response_model=List[NFCRecordResponse])
async def get_records_for_tag(
    tag_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all records for a specific NFC tag.
    
    Returns a list of all NFC records associated with the specified tag.
    """
    logger.info(f"Retrieving NFC records for tag with ID: {tag_id}")
    
    # Check if tag exists
    tag = db.query(NFCTag).filter(NFCTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NFC tag with ID {tag_id} not found"
        )
    
    records = db.query(NFCRecord).filter(NFCRecord.tag_id == tag_id).all()
    return records
