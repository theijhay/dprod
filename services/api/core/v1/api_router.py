"""API v1 Router - Central router for all API endpoints."""
from fastapi import APIRouter
from .routes import (
    auth,
    projects,
    deployments,
    health,
    ai,
    omniagent
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth")
router.include_router(projects.router, prefix="/projects")
router.include_router(deployments.router, prefix="/deployments")
router.include_router(health.router)
router.include_router(ai.router)
router.include_router(omniagent.router)
