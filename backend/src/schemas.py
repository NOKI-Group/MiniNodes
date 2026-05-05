from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    graph: dict = {"nodes": [], "edges": []}


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    graph: Optional[dict] = None


class WorkflowRead(BaseModel):
    id: str
    name: str
    description: Optional[str]
    active: bool
    graph: dict
    webhook_path: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExecutionRead(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger: Optional[str]
    input_data: Optional[Any]
    node_results: dict
    error: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
