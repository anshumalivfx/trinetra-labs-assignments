"""
Agent Output Model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AgentOutput(Base):
    """Agent execution output model"""

    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    # Agent info
    agent_name = Column(String, nullable=False, index=True)
    agent_role = Column(String, nullable=False)

    # Output
    output_data = Column(JSON, nullable=False)
    raw_output = Column(Text, nullable=True)

    # Execution details
    execution_time_ms = Column(Integer, nullable=True)
    token_usage = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    job = relationship("Job", back_populates="agent_outputs")
