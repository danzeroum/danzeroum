"""Danzeroum Tracker API — FastAPI wrapper over the tracker core."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import alerts, calc, certificates, clients, collect, config, documents, proposals, report, tenders

app = FastAPI(
    title="Danzeroum Tracker API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: allow the Vite dev server and any deployed origin.
# In production, restrict allow_origins to the actual deployed domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenders.router)
app.include_router(collect.router)
app.include_router(report.router)
app.include_router(config.router)
app.include_router(alerts.router)
app.include_router(calc.router)
app.include_router(certificates.router)
app.include_router(clients.router)
app.include_router(documents.router)
app.include_router(proposals.router)


@app.get("/health")
def health():
    return {"status": "ok"}
