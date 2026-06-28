"""Mutable config overrides stored in config_store.json.

Reads on every request (lightweight JSON file); merges over env-based Settings.
SMTP secrets are never exposed via GET /config.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_STORE = Path(__file__).parent / "config_store.json"

_ALLOWED_KEYS = {
    "sources",
    "modalidades",
    "proposal_horizon_days",
    "uf",
    "keywords",
    "scorer",
    "collect_interval_hours",
    "min_fit_alert",
    "page_size",
    "max_pages",
}


def load_overrides() -> dict[str, Any]:
    if _STORE.exists():
        try:
            return json.loads(_STORE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_overrides(patch: dict[str, Any]) -> None:
    current = load_overrides()
    for k, v in patch.items():
        if k in _ALLOWED_KEYS and v is not None:
            current[k] = v
    _STORE.write_text(json.dumps(current, ensure_ascii=False, indent=2))
