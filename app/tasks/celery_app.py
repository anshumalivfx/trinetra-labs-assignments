"""
Celery Application Configuration
"""

from celery import Celery

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "agent_orchestration",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.document_tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.WORKER_TIMEOUT,
    task_soft_time_limit=settings.WORKER_TIMEOUT - 30,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)
