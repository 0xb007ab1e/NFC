"""
Test helpers for the NFC Reader/Writer System PC Server.

This module provides helper functions to create test resources quickly
via ORM when routes under test require existing resources.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from sqlalchemy.orm import Session

from server.db.models.user import User
from server.db.models.device import Device
from server.db.models.connection import Connection
from server.db.models.nfc_tag import NFCTag
from server.db.models.nfc_record import NFCRecord


def create_test_user(
    db: Session,
    username: str = "testuser",
    email: str = "test@example.com",
    password_hash: str = "hashed_password",
    is_active: bool = True,
    is_admin: bool = False,
    permissions: List[str] = None,
    first_name: str = "Test",
    last_name: str = "User",
    notes: str = "Test user created for unit testing",
    user_metadata: Dict[str, Any] = None,
    commit: bool = True,
) -> User:
    """
    Create a test user via ORM.

    Args:
        db: Database session
        username: User's username
        email: User's email
        password_hash: Hashed password
        is_active: Whether the user is active
        is_admin: Whether the user is an admin
        permissions: List of permissions
        first_name: User's first name
        last_name: User's last name
        notes: Additional notes
        user_metadata: Additional user metadata
        commit: Whether to commit the transaction

    Returns:
        User: Created user instance
    """
    if permissions is None:
        permissions = ["read", "write"]
    if user_metadata is None:
        user_metadata = {"department": "Testing"}

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=is_active,
        is_admin=is_admin,
        permissions=permissions,
        first_name=first_name,
        last_name=last_name,
        notes=notes,
        user_metadata=user_metadata,
    )
    db.add(user)
    if commit:
        db.commit()
        db.refresh(user)
    return user


def create_test_device(
    db: Session,
    device_id: str = f"test-device-{uuid.uuid4().hex[:8]}",
    name: str = "Test Android Device",
    model: str = "Test Model X",
    manufacturer: str = "Test Manufacturer",
    android_version: str = "11.0",
    app_version: str = "1.2.3",
    supports_nfc: bool = True,
    supports_ndef: bool = True,
    is_active: bool = True,
    last_connection_type: Optional[str] = None,
    device_info: Dict[str, Any] = None,
    notes: str = "Test device created for unit testing",
    commit: bool = True,
) -> Device:
    """
    Create a test device via ORM.

    Args:
        db: Database session
        device_id: Unique device identifier
        name: Device name
        model: Device model
        manufacturer: Device manufacturer
        android_version: Android OS version
        app_version: App version
        supports_nfc: Whether the device supports NFC
        supports_ndef: Whether the device supports NDEF
        is_active: Whether the device is active
        last_connection_type: Last connection type used
        device_info: Additional device information
        notes: Additional notes
        commit: Whether to commit the transaction

    Returns:
        Device: Created device instance
    """
    if device_info is None:
        device_info = {"test_device": True, "created_for_testing": True}

    device = Device(
        device_id=device_id,
        name=name,
        model=model,
        manufacturer=manufacturer,
        android_version=android_version,
        app_version=app_version,
        supports_nfc=supports_nfc,
        supports_ndef=supports_ndef,
        is_active=is_active,
        last_connection_type=last_connection_type,
        device_info=device_info,
        notes=notes,
    )
    db.add(device)
    if commit:
        db.commit()
        db.refresh(device)
    return device


def create_test_connection(
    db: Session,
    device: Optional[Device] = None,
    user: Optional[User] = None,
    connection_type: str = "USB",
    connected_at: datetime = None,
    disconnected_at: Optional[datetime] = None,
    is_active: bool = True,
    ip_address: Optional[str] = None,
    port: Optional[str] = None,
    usb_serial: Optional[str] = None,
    connection_info: Dict[str, Any] = None,
    notes: str = "Test connection created for unit testing",
    commit: bool = True,
) -> Connection:
    """
    Create a test connection via ORM.

    Args:
        db: Database session
        device: Device instance (will create one if None)
        user: User instance (can be None)
        connection_type: Type of connection (USB, WiFi, Bluetooth, etc.)
        connected_at: Connection timestamp
        disconnected_at: Disconnection timestamp (None if still connected)
        is_active: Whether the connection is active
        ip_address: IP address (for WiFi connections)
        port: Port number (for WiFi connections)
        usb_serial: USB serial number (for USB connections)
        connection_info: Additional connection information
        notes: Additional notes
        commit: Whether to commit the transaction

    Returns:
        Connection: Created connection instance
    """
    if device is None:
        device = create_test_device(db, commit=True)
    
    if connected_at is None:
        connected_at = datetime.utcnow()
        
    if connection_info is None:
        connection_info = {"test_connection": True}
        
    # Set appropriate connection details based on type
    if connection_type == "USB" and usb_serial is None:
        usb_serial = f"TEST-USB-{uuid.uuid4().hex[:8]}"
    elif connection_type == "WiFi" and ip_address is None:
        ip_address = "192.168.1.100"
        port = "8080"

    connection = Connection(
        device_id=device.id,
        user_id=user.id if user else None,
        connection_type=connection_type,
        connected_at=connected_at,
        disconnected_at=disconnected_at,
        is_active=is_active,
        ip_address=ip_address,
        port=port,
        usb_serial=usb_serial,
        connection_info=connection_info,
        notes=notes,
    )
    db.add(connection)
    
    # Update device's last connection type
    if device.last_connection_type != connection_type:
        device.last_connection_type = connection_type
    
    if commit:
        db.commit()
        db.refresh(connection)
    return connection


def create_test_nfc_tag(
    db: Session,
    device: Optional[Device] = None,
    uid: str = None,
    tech_list: List[str] = None,
    tag_type: str = "TYPE4",
    is_writable: bool = True,
    is_ndef_formatted: bool = True,
    max_size: int = 8192,
    read_timestamp: datetime = None,
    read_location: Dict[str, float] = None,
    notes: str = "Test NFC tag created for unit testing",
    custom_data: Dict[str, Any] = None,
    commit: bool = True,
) -> NFCTag:
    """
    Create a test NFC tag via ORM.

    Args:
        db: Database session
        device: Device instance (will create one if None)
        uid: Unique identifier for the tag
        tech_list: List of NFC technologies supported
        tag_type: Type of NFC tag
        is_writable: Whether the tag is writable
        is_ndef_formatted: Whether the tag is NDEF formatted
        max_size: Maximum size in bytes
        read_timestamp: Timestamp when the tag was read
        read_location: Location where the tag was read
        notes: Additional notes
        custom_data: Custom tag data
        commit: Whether to commit the transaction

    Returns:
        NFCTag: Created NFCTag instance
    """
    if device is None:
        device = create_test_device(db, commit=True)
    
    if uid is None:
        uid = f"04{uuid.uuid4().hex[:12].upper()}"
        
    if tech_list is None:
        tech_list = ["android.nfc.tech.IsoDep", "android.nfc.tech.NfcA"]
        
    if read_timestamp is None:
        read_timestamp = datetime.utcnow()
        
    if read_location is None:
        read_location = {"latitude": 37.7749, "longitude": -122.4194}
        
    if custom_data is None:
        custom_data = {"test_field": "test_value"}
    
    tag = NFCTag(
        uid=uid,
        tech_list=tech_list,
        tag_type=tag_type,
        is_writable=is_writable,
        is_ndef_formatted=is_ndef_formatted,
        max_size=max_size,
        read_timestamp=read_timestamp,
        read_location=read_location,
        device_id=device.id,
        notes=notes,
        custom_data=custom_data,
    )
    db.add(tag)
    if commit:
        db.commit()
        db.refresh(tag)
    return tag


def create_test_nfc_record(
    db: Session,
    tag: NFCTag,
    tnf: int = 1,  # 1 = WELL_KNOWN (using integer value rather than string)
    record_type: str = "T",
    payload_str: str = "Hello, World!",
    record_index: int = 0,
    parsed_data: Dict[str, Any] = None,
    notes: str = "Test NFC record created for unit testing",
    commit: bool = True,
) -> NFCRecord:
    """
    Create a test NFC record via ORM.

    Args:
        db: Database session
        tag: NFCTag instance
        tnf: Type Name Format (TNF)
        record_type: Record type
        payload_str: String payload
        record_index: Index in the NDEF message
        parsed_data: Parsed data from the record
        notes: Additional notes
        commit: Whether to commit the transaction

    Returns:
        NFCRecord: Created NFCRecord instance
    """
    if parsed_data is None:
        parsed_data = {"text": "Hello, World!", "language": "en"}
    
    record = NFCRecord(
        tag_id=tag.id,
        tnf=tnf,
        type=record_type,
        payload_str=payload_str,
        record_index=record_index,
        parsed_data=parsed_data
        # Note: NFCRecord model doesn't have a 'notes' field
    )
    db.add(record)
    if commit:
        db.commit()
        db.refresh(record)
    return record


def create_related_resources(
    db: Session,
    create_user: bool = True,
    create_device: bool = True,
    create_connection: bool = True,
    create_tag: bool = False,
    create_record: bool = False,
    commit: bool = True,
) -> Dict[str, Any]:
    """
    Create a related set of test resources in a single operation.

    This is useful when testing endpoints that require a complete
    set of related resources to be present.

    Args:
        db: Database session
        create_user: Whether to create a user
        create_device: Whether to create a device
        create_connection: Whether to create a connection
        create_tag: Whether to create an NFC tag
        create_record: Whether to create an NFC record
        commit: Whether to commit the transaction

    Returns:
        Dict: Dictionary containing all created resources
    """
    result = {}
    
    # Create resources in the right order to maintain relationships
    if create_user:
        result["user"] = create_test_user(db, commit=commit)
    
    if create_device:
        result["device"] = create_test_device(db, commit=commit)
    
    if create_connection and "device" in result:
        result["connection"] = create_test_connection(
            db, 
            device=result["device"],
            user=result.get("user"),
            commit=commit
        )
    
    if create_tag and "device" in result:
        result["tag"] = create_test_nfc_tag(
            db,
            device=result["device"],
            commit=commit
        )
        
        if create_record and "tag" in result:
            result["record"] = create_test_nfc_record(
                db,
                tag=result["tag"],
                commit=commit
            )
    
    if commit:
        db.commit()
    
    return result
