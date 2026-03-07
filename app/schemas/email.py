"""
Email Schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any


class EmailBase(BaseModel):
    """Base email schema"""
    to_email: EmailStr
    subject: str
    body: str


class EmailCreate(EmailBase):
    """Email creation schema"""
    job_id: int


class EmailResponse(BaseModel):
    """Email response schema"""
    id: int
    job_id: int
    to_email: str
    from_email: str
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime] = None
    provider_message_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
