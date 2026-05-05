from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum
from sqlalchemy.sql import func
import enum
from src.database import Base


class ExecutionStatus(str, enum.Enum):
    running = "running"
    success = "success"
    error = "error"


class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False, index=True)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.running)

    trigger = Column(String, nullable=True)  # "webhook", "manual", "schedule"
    input_data = Column(JSON, nullable=True)

    # Per-node results: { node_id: { output: {...}, error: "..." } }
    node_results = Column(JSON, nullable=False, default=dict)
    error = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
