"""
Job Status and Management Routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.dependencies import get_db
from app.core.logging import get_logger
from app.models.job import Job
from app.models.agent_output import AgentOutput
from app.models.email import EmailRecord
from app.models.execution_log import ExecutionLog
from app.schemas.job import JobResponse, JobDetailResponse, JobStatusResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Get job status and details

    Returns complete job information including:
    - Current status
    - Execution time
    - Agent outputs
    - Email records
    - Execution logs
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get related data
    agent_outputs = db.query(AgentOutput).filter(AgentOutput.job_id == job.id).all()
    email_records = db.query(EmailRecord).filter(EmailRecord.job_id == job.id).all()
    execution_logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.job_id == job.id)
        .order_by(ExecutionLog.created_at)
        .all()
    )

    # Convert to dict for response
    job_dict = {
        "id": job.id,
        "job_id": job.job_id,
        "user_id": job.user_id,
        "document_id": job.document_id,
        "status": job.status,
        "retry_count": job.retry_count,
        "max_retries": job.max_retries,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "execution_time_ms": job.execution_time_ms,
        "result": job.result,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "agent_outputs": [
            {
                "agent_name": ao.agent_name,
                "agent_role": ao.agent_role,
                "output_data": ao.output_data,
                "execution_time_ms": ao.execution_time_ms,
                "created_at": ao.created_at,
            }
            for ao in agent_outputs
        ],
        "email_records": [
            {
                "to_email": er.to_email,
                "subject": er.subject,
                "status": er.status,
                "sent_at": er.sent_at,
                "error_message": er.error_message,
            }
            for er in email_records
        ],
        "execution_logs": [
            {
                "level": el.level,
                "step": el.step,
                "message": el.message,
                "metadata": el.log_metadata,
                "created_at": el.created_at,
            }
            for el in execution_logs
        ],
    }

    return job_dict


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Get quick job status

    Lightweight endpoint for polling job status
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate progress percentage
    progress = None
    if job.status == "PENDING":
        progress = 0
    elif job.status == "PROCESSING":
        progress = 50
    elif job.status in ["COMPLETED", "FAILED"]:
        progress = 100

    message = None
    if job.status == "PENDING":
        message = "Job is queued for processing"
    elif job.status == "PROCESSING":
        message = "Job is currently being processed"
    elif job.status == "COMPLETED":
        message = "Job completed successfully"
    elif job.status == "FAILED":
        message = f"Job failed: {job.error_message}"

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=progress,
        message=message,
        result=job.result if job.status == "COMPLETED" else None,
    )


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List jobs with optional filters

    Filters:
    - user_id: Filter by user
    - status: Filter by job status
    """
    query = db.query(Job)

    if user_id:
        query = query.filter(Job.user_id == user_id)

    if status:
        query = query.filter(Job.status == status)

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    return jobs
