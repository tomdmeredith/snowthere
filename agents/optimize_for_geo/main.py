"""FastAPI app for optimize_for_geo agent with IACP endpoints."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException

from .agent import OptimizeForGeoAgent
from .schemas import (
    AgentIdentity,
    ObjectiveRequest,
    ObjectiveResponse,
    ObjectiveStatus,
    ToolManifest,
)

app = FastAPI(
    title="Optimize for GEO Agent",
    description="Enhances resort content for AI citation and search engine optimization",
    version="0.1.0",
)

# In-memory storage for objectives
objectives: dict[str, dict[str, Any]] = {}


@app.get("/", response_model=AgentIdentity)
async def get_identity() -> AgentIdentity:
    """
    GET / - Agent identity.

    Returns basic information about this agent.
    """
    return AgentIdentity()


@app.get("/tools", response_model=ToolManifest)
async def get_tools() -> ToolManifest:
    """
    GET /tools - Tool manifest.

    Returns the input/output schema for this agent's capabilities.
    """
    return ToolManifest()


@app.post("/objectives", response_model=ObjectiveResponse)
async def create_objective(
    request: ObjectiveRequest,
    background_tasks: BackgroundTasks,
) -> ObjectiveResponse:
    """
    POST /objectives - Create a new optimization objective.

    Starts an asynchronous GEO optimization task.
    Returns immediately with an objective ID to poll for status.
    """
    objective_id = str(uuid4())
    created_at = datetime.utcnow()

    # Store initial objective state
    objectives[objective_id] = {
        "id": objective_id,
        "status": ObjectiveStatus.PENDING,
        "created_at": created_at,
        "started_at": None,
        "completed_at": None,
        "input": request.input,
        "result": None,
        "error": None,
    }

    # Start background task
    background_tasks.add_task(
        _execute_optimization,
        objective_id,
        request.input,
    )

    return ObjectiveResponse(
        id=objective_id,
        status=ObjectiveStatus.PENDING,
        created_at=created_at,
    )


@app.get("/objectives/{objective_id}", response_model=ObjectiveResponse)
async def get_objective(objective_id: str) -> ObjectiveResponse:
    """
    GET /objectives/{id} - Poll objective status.

    Returns the current status and result (if completed) of an optimization objective.
    """
    if objective_id not in objectives:
        raise HTTPException(status_code=404, detail="Objective not found")

    obj = objectives[objective_id]

    return ObjectiveResponse(
        id=obj["id"],
        status=obj["status"],
        created_at=obj["created_at"],
        started_at=obj["started_at"],
        completed_at=obj["completed_at"],
        result=obj["result"],
        error=obj["error"],
    )


async def _execute_optimization(objective_id: str, input_data: Any) -> None:
    """
    Execute GEO optimization in background task.

    Updates objective state as optimization progresses.
    """
    # Update to processing
    objectives[objective_id]["status"] = ObjectiveStatus.PROCESSING
    objectives[objective_id]["started_at"] = datetime.utcnow()

    try:
        # Create agent and run optimization
        agent = OptimizeForGeoAgent(task_id=objective_id)
        result = await agent.optimize(input_data)

        # Update with success
        objectives[objective_id]["status"] = ObjectiveStatus.COMPLETED
        objectives[objective_id]["completed_at"] = datetime.utcnow()
        objectives[objective_id]["result"] = result

    except Exception as e:
        # Update with failure
        objectives[objective_id]["status"] = ObjectiveStatus.FAILED
        objectives[objective_id]["completed_at"] = datetime.utcnow()
        objectives[objective_id]["error"] = str(e)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for Railway/deployment monitoring."""
    return {"status": "healthy", "agent": "optimize_for_geo"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
