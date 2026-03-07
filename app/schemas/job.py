"""
Job Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class JobStatusEnum(str, Enum):
    """Job status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class JobBase(BaseModel):
    """Base job schema"""
    job_id: str


class JobCreate(BaseModel):
    """Job creation schema"""
    user_id: int
    document_id: int


class JobResponse(BaseModel):
    """Job response schema"""
    id: int
    job_id: str
    user_id: int
    document_id: int
    status: str
    retry_count: int
    max_retries: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Detailed job response with related data"""
    agent_outputs: Optional[List[Dict[str, Any]]] = None
    email_records: Optional[List[Dict[str, Any]]] = None
    execution_logs: Optional[List[Dict[str, Any]]] = None


class JobStatusResponse(BaseModel):
    """Job status check response"""
    job_id: str
    status: str
    progress: Optional[int] = None  # 0-100
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
