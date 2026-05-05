from fastapi import APIRouter
from src.nodes.base import registry
import src.nodes.core  # ensures core nodes are registered

router = APIRouter(prefix="/nodes", tags=["nodes"])


@router.get("/")
def get_nodes():
    return registry.all()
