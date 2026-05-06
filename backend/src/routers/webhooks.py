from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from src.database import get_db
from src.models.workflow import Workflow
from src.models.execution import Execution
from src.services.execution_engine import engine as exec_engine

router = APIRouter(tags=["webhooks"])


def _resolve_webhook_path(wf: Workflow, path: str) -> bool:
    """
    Returns True if the incoming path matches either:
    - the workflow's default webhook_path  (e.g. /webhook/abc123)
    - a custom_path configured on a webhook trigger node  (e.g. /webhook/my-custom)
    """
    full_path = f"/webhook/{path}"

    if wf.webhook_path == full_path:
        return True

    # Check nodes for a custom_path override
    nodes = (wf.graph or {}).get("nodes", [])
    for node in nodes:
        if node.get("type") == "core.webhook_trigger":
            custom = node.get("data", {}).get("config", {}).get("custom_path", "").strip().strip("/")
            if custom and f"/webhook/{custom}" == full_path:
                return True

    return False


@router.api_route("/webhook/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def receive_webhook(path: str, request: Request, db: Session = Depends(get_db)):
    # Find all active workflows and check if any matches this path
    active_workflows = db.query(Workflow).filter(Workflow.active == True).all()  # noqa: E712

    wf = None
    for candidate in active_workflows:
        if _resolve_webhook_path(candidate, path):
            wf = candidate
            break

    if not wf:
        raise HTTPException(status_code=404, detail="No workflow found for this webhook")

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

    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=500, detail="Execution not found after run")

    node_results = execution.node_results or {}
    for result in node_results.values():
        out = result.get("output")
        if isinstance(out, dict) and out.get("_output"):
            return JSONResponse(content=out.get("data"))

    return JSONResponse(content={
        "execution_id": execution_id,
        "status": execution.status,
        "node_results": node_results,
    })