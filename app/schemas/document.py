"""
Document Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    """Base document schema"""

    filename: str
    original_filename: str


class DocumentCreate(DocumentBase):
    """Document creation schema"""

    pass


class DocumentMetadata(BaseModel):
    """Document metadata schema"""

    page_count: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Document response schema"""

    id: int
    user_id: int
    file_size: int
    mime_type: str
    checksum: str
    page_count: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Document upload response"""

    document: DocumentResponse
    job_id: str
    message: str
