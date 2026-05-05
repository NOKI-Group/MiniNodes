from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.database import engine, Base
from src.routers import workflows, executions, webhooks, nodes as nodes_router
from src.services.execution_engine import engine as exec_engine

import src.models.workflow
import src.models.execution


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    await exec_engine.start()
    yield
    await exec_engine.stop()


app = FastAPI(title="MiniNodes API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows.router)
app.include_router(executions.router)
app.include_router(webhooks.router)
app.include_router(nodes_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}