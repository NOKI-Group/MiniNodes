from sqlalchemy import Column, String, Integer, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from src.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True)  # uuid
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    active = Column(Boolean, default=False)

    # The full graph: nodes + edges as stored by Vue Flow
    graph = Column(JSON, nullable=False, default=lambda: {"nodes": [], "edges": []})

    webhook_path = Column(String, nullable=True, unique=True)  # e.g. /webhook/abc123

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
