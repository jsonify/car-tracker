"""FastAPI application entry point for the Car Tracker web dashboard."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.backend.routers import analytics, bookings, runs, vehicles

app = FastAPI(title="Car Tracker Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(runs.router, prefix="/runs", tags=["runs"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
app.include_router(analytics.router, tags=["analytics"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
