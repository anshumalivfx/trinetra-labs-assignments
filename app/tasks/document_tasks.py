"""
Document Processing Tasks
Background tasks for PDF processing and email sending
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from app.tasks.celery_app import celery_app
from app.core.database import get_db_context
from app.core.logging import get_logger
from app.models.job import Job, JobStatus
from app.models.document import Document
from app.models.agent_output import AgentOutput
from app.models.email import EmailRecord, EmailStatus
from app.models.execution_log import ExecutionLog
from app.services.pdf_service import PDFService
from app.services.orchestration_service import OrchestrationService

logger = get_logger(__name__)


def log_execution(
    db, job_id: int, level: str, step: str, message: str, metadata: Dict = None
):
    """Helper to log execution steps"""
    log_entry = ExecutionLog(
        job_id=job_id,
        level=level,
        step=step,
        message=message,
        log_metadata=metadata or {},
    )
    db.add(log_entry)
    db.commit()


@celery_app.task(bind=True, name="process_document")
def process_document_task(
    self,
    job_id: str,
    document_id: int,
    user_id: int,
    recipient_email: str,
):
    """
    Process document: extract content, run agents, send email

    Args:
        job_id: Unique job identifier
        document_id: Document ID to process
        user_id: User ID
        recipient_email: Email recipient
    """
    with get_db_context() as db:
        try:
            # Get job
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if not job:
                logger.error("job_not_found", job_id=job_id)
                return {"success": False, "error": "Job not found"}

            # Update job status
            job.status = JobStatus.PROCESSING.value
            job.started_at = datetime.utcnow()
            db.commit()

            log_execution(
                db,
                job.id,
                "INFO",
                "job_started",
                f"Processing started for document {document_id}",
            )

            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise Exception(f"Document {document_id} not found")

            log_execution(
                db,
                job.id,
                "INFO",
                "document_loaded",
                f"Document loaded: {document.filename}",
            )

            # Extract PDF content
            logger.info(
                "extracting_pdf_content", job_id=job_id, document_id=document_id
            )

            # Run async extraction in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            pdf_content = loop.run_until_complete(
                PDFService.extract_content(document.file_path)
            )

            log_execution(
                db,
                job.id,
                "INFO",
                "pdf_extracted",
                f"Extracted {len(pdf_content.get('pages', []))} pages",
                {"page_count": len(pdf_content.get("pages", []))},
            )

            # Run agent orchestration
            logger.info("starting_orchestration", job_id=job_id)

            orchestration_result = loop.run_until_complete(
                OrchestrationService.process_document_and_send_email(
                    pdf_content=pdf_content,
                    recipient_email=recipient_email,
                    document_id=document_id,
                    job_id=job_id,
                )
            )

            loop.close()

            # Save agent outputs
            stages = orchestration_result.get("stages", {})

            for stage_name, stage_data in stages.items():
                if stage_name in [
                    "pdf_analysis",
                    "email_composition",
                    "email_validation",
                ]:
                    agent_output = AgentOutput(
                        job_id=job.id,
                        agent_name=stage_data.get("agent_name", stage_name),
                        agent_role=stage_name,
                        output_data=stage_data.get("data", {}),
                        raw_output=str(stage_data),
                        execution_time_ms=stage_data.get("execution_time_ms", 0),
                    )
                    db.add(agent_output)

            db.commit()

            log_execution(
                db,
                job.id,
                "INFO",
                "agents_completed",
                "All agents completed successfully",
            )

            # Save email record
            email_stage = stages.get("email_composition", {})
            email_delivery = stages.get("email_delivery", {})

            email_data = email_stage.get("data", {})

            email_record = EmailRecord(
                job_id=job.id,
                to_email=recipient_email,
                from_email="noreply@trinetralabs.ai",
                subject=email_data.get("subject", "Document Analysis"),
                body=email_data.get("body", ""),
                status=(
                    EmailStatus.SENT.value
                    if email_delivery.get("success")
                    else EmailStatus.FAILED.value
                ),
                sent_at=datetime.utcnow() if email_delivery.get("success") else None,
                provider_message_id=email_delivery.get("message_id"),
                provider_response=email_delivery,
                error_message=(
                    email_delivery.get("error")
                    if not email_delivery.get("success")
                    else None
                ),
            )
            db.add(email_record)
            db.commit()

            # Update job with final status
            job.status = (
                JobStatus.COMPLETED.value
                if orchestration_result.get("success")
                else JobStatus.FAILED.value
            )
            job.completed_at = datetime.utcnow()
            job.execution_time_ms = orchestration_result.get("execution_time_ms", 0)
            job.result = orchestration_result

            if not orchestration_result.get("success"):
                job.error_message = orchestration_result.get("error", "Unknown error")

            # Mark document as processed
            document.is_processed = True

            db.commit()

            log_execution(
                db,
                job.id,
                "INFO",
                "job_completed",
                f"Job completed with status: {job.status}",
            )

            logger.info(
                "document_processing_completed",
                job_id=job_id,
                status=job.status,
                execution_time_ms=job.execution_time_ms,
            )

            return {
                "success": True,
                "job_id": job_id,
                "status": job.status,
                "result": orchestration_result,
            }

        except Exception as e:
            logger.error(
                "document_processing_failed",
                job_id=job_id,
                error=str(e),
                exc_info=True,
            )

            # Update job with error
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = JobStatus.FAILED.value
                job.completed_at = datetime.utcnow()
                job.error_message = str(e)
                db.commit()

                log_execution(
                    db, job.id, "ERROR", "job_failed", f"Job failed: {str(e)}"
                )

            # Retry logic
            if self.request.retries < self.max_retries:
                logger.info(
                    "retrying_task",
                    job_id=job_id,
                    retry_count=self.request.retries + 1,
                )
                raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))

            return {
                "success": False,
                "job_id": job_id,
                "error": str(e),
            }
