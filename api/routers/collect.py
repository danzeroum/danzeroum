"""Collection pipeline endpoints.

POST /collect  → 202 + run_id (starts background task)
GET  /collect/{run_id} → polling: status=running|done|error + result
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.deps import get_settings
from api.schemas import CollectionRunStatus

router = APIRouter(prefix="/collect", tags=["collect"])

# In-memory run registry (single-process V1; fine for the operational single-user context)
_runs: dict[str, dict[str, Any]] = {}


def _execute_collection(run_id: str) -> None:
    cfg = get_settings()
    try:
        from danzeroum_tracker.pipeline import run_collection
        from danzeroum_tracker.storage.postgres import PostgresRepository

        repo = PostgresRepository(cfg.database_url)
        result = run_collection(cfg, repo)
        _runs[run_id] = {"status": "done", "result": result.to_dict()}
    except Exception as exc:  # noqa: BLE001
        _runs[run_id] = {"status": "error", "result": {"error": str(exc)}}


@router.post("", status_code=202, response_model=CollectionRunStatus)
def start_collection(background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    _runs[run_id] = {"status": "running", "result": None}
    background_tasks.add_task(_execute_collection, run_id)
    return {"run_id": run_id, "status": "running", "result": None}


@router.get("/{run_id}", response_model=CollectionRunStatus)
def get_run_status(run_id: str):
    run = _runs.get(run_id)
    if run is None:
        raise HTTPException(404, "Run não encontrado")
    return {"run_id": run_id, **run}


@router.get("", response_model=list[dict])
def list_runs():
    """Return all run IDs and their statuses (most recent last)."""
    return [{"run_id": k, **v} for k, v in _runs.items()]
