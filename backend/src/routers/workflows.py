import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.workflow import Workflow
from src.schemas import WorkflowCreate, WorkflowUpdate, WorkflowRead
from src.services.execution_engine import engine as exec_engine

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=List[WorkflowRead])
def get_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/", response_model=WorkflowRead, status_code=201)
def create_workflow(data: WorkflowCreate, db: Session = Depends(get_db)):
    wf = Workflow(
        id=str(uuid.uuid4()),
        name=data.name,
        description=data.description,
        graph=data.graph,
        webhook_path=f"/webhook/{uuid.uuid4().hex[:12]}",
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.patch("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(workflow_id: str, data: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(wf, key, value)
    db.commit()
    db.refresh(wf)
    return wf


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    execution_id = await exec_engine.run(
        workflow_id=wf.id,
        graph=wf.graph,
        trigger="manual",
        input_data={},
    )
    return {"execution_id": execution_id}
