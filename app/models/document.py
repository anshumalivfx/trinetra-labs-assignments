"""
Document Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Document(Base):
    """Document/PDF upload model"""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)  # in bytes
    mime_type = Column(String, nullable=False)
    checksum = Column(String, nullable=False, index=True)  # SHA256 hash
    
    # Metadata
    page_count = Column(Integer, nullable=True)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    
    # Status
    is_processed = Column(String, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    jobs = relationship("Job", back_populates="document", cascade="all, delete-orphan")
