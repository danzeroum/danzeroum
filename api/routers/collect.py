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
        from danzeroum_tracker.cli import build_adapters
        from danzeroum_tracker.notifications import build_notifier
        from danzeroum_tracker.pipeline import run_collection
        from danzeroum_tracker.scoring import get_scorer
        from danzeroum_tracker.storage import build_repository

        repo = build_repository(cfg.database_url)
        adapters = build_adapters(cfg)
        scorer = get_scorer(cfg.scorer)
        notifier = build_notifier(cfg)
        result = run_collection(adapters, repo, scorer, min_fit_alert=cfg.min_fit_alert)
        payload = result.to_dict()
        try:
            payload["notified"] = notifier.notify(payload)
        except Exception as exc:  # noqa: BLE001
            payload["notified"] = 0
            payload["notify_error"] = str(exc)
        _runs[run_id] = {"status": "done", "result": payload}
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
