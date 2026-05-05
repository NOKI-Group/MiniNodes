from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from src.database import get_db
from src.models.workflow import Workflow
from src.services.execution_engine import engine as exec_engine

router = APIRouter(tags=["webhooks"])


@router.api_route("/webhook/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def receive_webhook(path: str, request: Request, db: Session = Depends(get_db)):
    full_path = f"/webhook/{path}"
    wf = db.query(Workflow).filter(Workflow.webhook_path == full_path).first()

    if not wf:
        raise HTTPException(status_code=404, detail="No workflow found for this webhook")

    if not wf.active:
        raise HTTPException(status_code=400, detail="Workflow is not active")

    # Parse incoming payload
    try:
        body = await request.json()
    except Exception:
        body = {}

    input_data = {
        "method": request.method,
        "headers": dict(request.headers),
        "query": dict(request.query_params),
        "body": body,
    }

    execution_id = await exec_engine.run(
        workflow_id=wf.id,
        graph=wf.graph,
        trigger="webhook",
        input_data=input_data,
    )

    return {"execution_id": execution_id, "status": "accepted"}
