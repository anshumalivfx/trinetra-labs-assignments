"""
Email Record Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.core.database import Base


class EmailStatus(str, Enum):
    """Email delivery status"""
    PENDING = "PENDING"
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"


class EmailRecord(Base):
    """Email record model"""
    
    __tablename__ = "email_records"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Email details
    to_email = Column(String, nullable=False, index=True)
    from_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    
    # Delivery status
    status = Column(String, default=EmailStatus.PENDING.value, index=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Provider response
    provider_message_id = Column(String, nullable=True, index=True)
    provider_response = Column(JSON, nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="email_records")
