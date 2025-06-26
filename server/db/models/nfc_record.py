"""
NFC Record model for the NFC Reader/Writer System PC Server.

This module contains the NFCRecord model for storing NFC record data.
"""

from typing import Optional
import uuid

from sqlalchemy import Column, Integer, String, Text, LargeBinary, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.db.models.base import BaseModel


class NFCRecord(BaseModel):
    """
    NFC Record model.
    
    This model represents a record within an NFC tag. An NFC tag can
    contain multiple records, each with different types and data.
    """

    # Record identification
    tnf = Column(Integer, nullable=False)  # Type Name Format
    type = Column(String(255), nullable=False, index=True)
    
    # Record data
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    payload = Column(LargeBinary, nullable=True)  # Binary payload data
    payload_str = Column(Text, nullable=True)  # String representation of payload if applicable
    
    # Tag relationship
    tag_id = Column(UUID(as_uuid=True), ForeignKey("nfc_tag.id"), nullable=False)
    tag = relationship("NFCTag", back_populates="records")
    
    # Record metadata
    record_index = Column(Integer, nullable=False)  # Position in the tag
    parsed_data = Column(JSON, nullable=True)  # Parsed data in JSON format
    
    def __repr__(self) -> str:
        """
        String representation of the NFC record.
        
        Returns:
            str: String representation.
        """
        return f"<NFCRecord(id={self.id}, type={self.type}, tnf={self.tnf})>"
        
    @property
    def mime_type(self) -> Optional[str]:
        """
        Get the MIME type if this is a MIME record.
        
        Returns:
            Optional[str]: MIME type or None.
        """
        if self.tnf == 2:  # MIME_MEDIA TNF
            return self.type
        return None
        
    @property
    def uri(self) -> Optional[str]:
        """
        Get the URI if this is a URI record.
        
        Returns:
            Optional[str]: URI or None.
        """
        if self.tnf == 3:  # ABSOLUTE_URI TNF
            return self.payload_str
        return None
        
    @property
    def text(self) -> Optional[str]:
        """
        Get the text if this is a TEXT record.
        
        Returns:
            Optional[str]: Text or None.
        """
        if self.tnf == 1 and self.type == "T":  # WELL_KNOWN TNF and TEXT type
            return self.payload_str
        return None
