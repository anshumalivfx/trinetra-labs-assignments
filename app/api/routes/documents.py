"""
Document Upload and Management Routes
"""
import uuid
import hashlib
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db
from app.core.logging import get_logger
from app.models.document import Document
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.pdf_service import PDFService
from app.tasks.document_tasks import process_document_task

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(..., description="PDF file to upload"),
    recipient_email: str = Form(..., description="Email recipient"),
    user_id: int = Form(1, description="User ID"),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF document for processing
    
    This endpoint:
    1. Validates the uploaded PDF
    2. Saves it to disk
    3. Extracts metadata
    4. Creates a background job
    5. Returns job ID for tracking
    """
    logger.info(
        "document_upload_started",
        filename=file.filename,
        content_type=file.content_type,
        user_id=user_id,
    )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate PDF
        try:
            validation_result = await PDFService.validate_pdf(
                file_content, file.filename
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Save file
        file_info = await PDFService.save_file(file_content, file.filename)
        
        # Extract metadata
        metadata = await PDFService.extract_metadata(file_info["file_path"])
        
        # Check for duplicate (by checksum)
        existing_doc = (
            db.query(Document)
            .filter(Document.checksum == file_info["checksum"])
            .first()
        )
        
        if existing_doc:
            logger.warning(
                "duplicate_document_detected",
                checksum=file_info["checksum"],
                existing_id=existing_doc.id,
            )
            # Still process it but log the duplicate
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=file_info["filename"],
            original_filename=file.filename,
            file_path=file_info["file_path"],
            file_size=file_info["size"],
            mime_type=file.content_type or "application/pdf",
            checksum=file_info["checksum"],
            page_count=metadata.get("page_count"),
            title=metadata.get("title"),
            author=metadata.get("author"),
            is_processed=False,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create job
        job_id = str(uuid.uuid4())
        job = Job(
            job_id=job_id,
            user_id=user_id,
            document_id=document.id,
            status=JobStatus.PENDING.value,
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Trigger background processing
        process_document_task.delay(
            job_id=job_id,
            document_id=document.id,
            user_id=user_id,
            recipient_email=recipient_email,
        )
        
        logger.info(
            "document_upload_completed",
            document_id=document.id,
            job_id=job_id,
            file_size=document.file_size,
        )
        
        return DocumentUploadResponse(
            document=document,
            job_id=job_id,
            message="Document uploaded successfully. Processing in background.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "document_upload_failed",
            filename=file.filename,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}",
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """Get document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    user_id: int = 1,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List documents for a user"""
    documents = (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return documents
