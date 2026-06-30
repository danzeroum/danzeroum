"""Danzeroum Tracker API — FastAPI wrapper over the tracker core."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth_middleware import require_auth
from api.routers import alerts, auth, calc, certificates, clients, collect, config, documents, proposals, report, score, tenders

_auth = [Depends(require_auth)]

app = FastAPI(
    title="Danzeroum Tracker API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Público
app.include_router(auth.router)

# Protegidos
app.include_router(tenders.router, dependencies=_auth)
app.include_router(collect.router, dependencies=_auth)
app.include_router(report.router, dependencies=_auth)
app.include_router(config.router, dependencies=_auth)
app.include_router(alerts.router, dependencies=_auth)
app.include_router(calc.router, dependencies=_auth)
app.include_router(certificates.router, dependencies=_auth)
app.include_router(clients.router, dependencies=_auth)
app.include_router(documents.router, dependencies=_auth)
app.include_router(proposals.router, dependencies=_auth)
app.include_router(score.router, dependencies=_auth)


@app.get("/health")
def health():
    return {"status": "ok"}
