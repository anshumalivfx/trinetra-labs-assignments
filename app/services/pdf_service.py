"""
PDF Processing Service
Handles PDF upload, validation, and extraction
"""
import os
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
import pdfplumber
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFService:
    """PDF processing service"""
    
    MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert to bytes
    
    @staticmethod
    async def validate_pdf(file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate PDF file
        
        Args:
            file_content: PDF file content
            filename: Original filename
            
        Returns:
            Validation result dict
            
        Raises:
            ValueError: If validation fails
        """
        # Check file size
        if len(file_content) > PDFService.MAX_FILE_SIZE:
            raise ValueError(
                f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            raise ValueError("File must be a PDF")
        
        # Check if it's a valid PDF
        try:
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            page_count = len(pdf_reader.pages)
            
            if page_count == 0:
                raise ValueError("PDF has no pages")
                
        except Exception as e:
            raise ValueError(f"Invalid PDF file: {str(e)}")
        
        return {
            "valid": True,
            "size": len(file_content),
            "page_count": page_count,
        }
    
    @staticmethod
    async def save_file(file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content
            filename: Original filename
            
        Returns:
            File metadata dict
        """
        # Create uploads directory if it doesn't exist
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        checksum = hashlib.sha256(file_content).hexdigest()[:16]
        unique_filename = f"{timestamp}_{checksum}_{filename}"
        
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(
            "file_saved",
            filename=filename,
            path=str(file_path),
            size=len(file_content),
        )
        
        return {
            "filename": unique_filename,
            "file_path": str(file_path),
            "checksum": hashlib.sha256(file_content).hexdigest(),
            "size": len(file_content),
        }
    
    @staticmethod
    async def extract_metadata(file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Metadata dict
        """
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                metadata = pdf_reader.metadata or {}
                page_count = len(pdf_reader.pages)
                
                return {
                    "page_count": page_count,
                    "title": metadata.get("/Title", None),
                    "author": metadata.get("/Author", None),
                    "subject": metadata.get("/Subject", None),
                    "creator": metadata.get("/Creator", None),
                    "producer": metadata.get("/Producer", None),
                }
        except Exception as e:
            logger.error("metadata_extraction_failed", file_path=file_path, error=str(e))
            return {"page_count": 0}
    
    @staticmethod
    async def extract_content(file_path: str) -> Dict[str, Any]:
        """
        Extract structured content from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted content dict with text, tables, etc.
        """
        try:
            extracted_data = {
                "text": "",
                "pages": [],
                "tables": [],
                "entities": [],
            }
            
            # Extract text using pdfplumber (better for tables)
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    
                    extracted_data["pages"].append({
                        "page_number": page_num,
                        "text": page_text,
                        "char_count": len(page_text),
                    })
                    
                    extracted_data["text"] += page_text + "\n"
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            extracted_data["tables"].append({
                                "page_number": page_num,
                                "table_index": table_idx,
                                "data": table,
                            })
            
            # Basic entity extraction (can be enhanced)
            extracted_data["entities"] = PDFService._extract_basic_entities(
                extracted_data["text"]
            )
            
            logger.info(
                "content_extracted",
                file_path=file_path,
                page_count=len(extracted_data["pages"]),
                table_count=len(extracted_data["tables"]),
                text_length=len(extracted_data["text"]),
            )
            
            return extracted_data
            
        except Exception as e:
            logger.error("content_extraction_failed", file_path=file_path, error=str(e))
            raise
    
    @staticmethod
    def _extract_basic_entities(text: str) -> list:
        """Extract basic entities like emails, phones, etc."""
        import re
        
        entities = []
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            entities.append({"type": "email", "value": email})
        
        # Extract phone numbers (basic pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            entities.append({"type": "phone", "value": phone})
        
        # Extract URLs
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            entities.append({"type": "url", "value": url})
        
        return entities
