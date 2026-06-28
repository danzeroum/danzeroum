from __future__ import annotations

from fastapi import APIRouter

from api.config_store import load_overrides, save_overrides
from api.deps import get_settings
from api.schemas import ConfigOut, ConfigPatch

router = APIRouter(prefix="/config", tags=["config"])


def _current_config() -> dict:
    cfg = get_settings()
    base: dict = {
        "sources": cfg.sources,
        "modalidades": cfg.modalidades,
        "proposal_horizon_days": cfg.proposal_horizon_days,
        "uf": cfg.uf,
        "keywords": cfg.keywords,
        "scorer": cfg.scorer,
        "collect_interval_hours": cfg.collect_interval_hours,
        "min_fit_alert": cfg.min_fit_alert,
        "page_size": cfg.page_size,
        "max_pages": cfg.max_pages,
    }
    overrides = load_overrides()
    for k, v in overrides.items():
        if k in base:
            base[k] = v
    return base


@router.get("", response_model=ConfigOut)
def get_config():
    return _current_config()


@router.put("", response_model=ConfigOut)
def update_config(patch: ConfigPatch):
    save_overrides(patch.model_dump(exclude_none=True))
    return _current_config()
