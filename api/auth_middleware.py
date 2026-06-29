"""Dependência require_auth para proteger routers."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from api.routers.auth import _verify_cookie


def require_auth(request: Request) -> str:
    username = _verify_cookie(request)
    if not username:
        raise HTTPException(401, "Não autenticado")
    return username
