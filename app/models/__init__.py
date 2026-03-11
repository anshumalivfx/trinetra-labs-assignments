"""Models Package"""

# Import all models to ensure they're registered with SQLAlchemy
from app.models.user import User
from app.models.document import Document
from app.models.job import Job
from app.models.email import EmailRecord
from app.models.execution_log import ExecutionLog
from app.models.agent_output import AgentOutput

__all__ = [
    "User",
    "Document",
    "Job",
    "EmailRecord",
    "ExecutionLog",
    "AgentOutput",
]
