"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Add database and Redis connectivity checks
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {"status": "alive"}
