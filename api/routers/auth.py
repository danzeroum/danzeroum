"""Autenticação single-tenant via cookie httpOnly."""

from __future__ import annotations

import os
from datetime import timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# Segredo default de desenvolvimento. É público (está aqui no repositório), então
# uma sessão assinada com ele é forjável por qualquer um — ver _secret_missing().
_DEV_SECRET = "dev-secret-change-me"

_SECRET = os.getenv("SESSION_SECRET", _DEV_SECRET)
_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "8"))
_USERNAME = os.getenv("AUTH_USERNAME", "admin")
_PASSWORD_HASH = os.getenv("AUTH_PASSWORD_HASH", "")
_COOKIE = "dz_session"

_signer = URLSafeTimedSerializer(_SECRET, salt="dz-session")


def _secret_missing() -> bool:
    """True quando a API caiu no segredo default — sessão não é confiável.

    Sem ``SESSION_SECRET`` no ambiente, o cookie ``dz_session`` seria assinado
    com um valor público e qualquer um poderia forjar uma sessão válida. Nesse
    estado a autenticação recusa tudo em vez de aceitar tudo.
    """
    return _SECRET == _DEV_SECRET


def _make_cookie(response: Response, username: str) -> None:
    token = _signer.dumps({"u": username})
    response.set_cookie(
        _COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=False,  # True em produção com HTTPS
        max_age=_TTL_HOURS * 3600,
    )


def _verify_cookie(request: Request) -> str | None:
    if _secret_missing():
        return None
    token = request.cookies.get(_COOKIE)
    if not token:
        return None
    try:
        data = _signer.loads(token, max_age=_TTL_HOURS * 3600)
        return data.get("u")
    except (BadSignature, SignatureExpired):
        return None


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginBody, response: Response):
    if _secret_missing():
        raise HTTPException(500, "SESSION_SECRET não configurado")
    if body.username != _USERNAME:
        raise HTTPException(401, "Credenciais inválidas")
    if not _PASSWORD_HASH:
        raise HTTPException(500, "AUTH_PASSWORD_HASH não configurado")
    if not bcrypt.checkpw(body.password.encode(), _PASSWORD_HASH.encode()):
        raise HTTPException(401, "Credenciais inválidas")
    _make_cookie(response, body.username)
    return {"user": {"username": body.username}}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(_COOKIE)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    username = _verify_cookie(request)
    if not username:
        raise HTTPException(401, "Não autenticado")
    return {"username": username}
