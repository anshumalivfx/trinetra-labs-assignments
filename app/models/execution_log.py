"""
Execution Log Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ExecutionLog(Base):
    """Execution log for debugging and observability"""
    
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Log details
    level = Column(String, nullable=False, index=True)  # INFO, WARNING, ERROR
    step = Column(String, nullable=False)  # e.g., "pdf_extraction", "agent_execution"
    message = Column(Text, nullable=False)
    
    # Additional context
    metadata = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    job = relationship("Job", back_populates="execution_logs")
