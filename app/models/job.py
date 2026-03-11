"""
Job Model - Tracks processing jobs
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from app.core.database import Base


class JobStatus(str, Enum):
    """Job status enumeration"""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class Job(Base):
    """Job model for tracking background processing"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(
        Integer, ForeignKey("documents.id"), nullable=False, index=True
    )

    # Status tracking
    status = Column(String, default=JobStatus.PENDING.value, index=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Execution details
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)

    # Results
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_traceback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="jobs")
    document = relationship("Document", back_populates="jobs")
    agent_outputs = relationship(
        "AgentOutput", back_populates="job", cascade="all, delete-orphan"
    )
    email_records = relationship(
        "EmailRecord", back_populates="job", cascade="all, delete-orphan"
    )
    execution_logs = relationship(
        "ExecutionLog", back_populates="job", cascade="all, delete-orphan"
    )
