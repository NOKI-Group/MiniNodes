from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.execution import Execution
from src.schemas import ExecutionRead

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("/", response_model=List[ExecutionRead])
def get_executions(workflow_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Execution)
    if workflow_id:
        q = q.filter(Execution.workflow_id == workflow_id)
    return q.order_by(Execution.started_at.desc()).limit(100).all()


@router.get("/{execution_id}", response_model=ExecutionRead)
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    ex = db.query(Execution).filter(Execution.id == execution_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ex
