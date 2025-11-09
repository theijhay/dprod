"""Main FastAPI application for Dprod API."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .utils.config import settings
from .v1.routes import auth, projects, deployments, health, ai, omniagent


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Dprod API Server...")
    
    print(f"🌐 API Server running on http://localhost:{settings.port}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Dprod API Server...")


# Create FastAPI app
app = FastAPI(
    title="Dprod API",
    description="Zero-configuration deployment platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Allow all hosts in staging if explicitly enabled to pass ALB host header.
if os.getenv("ALLOW_ALL_HOSTS", "false").lower() != "true":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai-monitoring"])
app.include_router(omniagent.router, prefix="/api/v1", tags=["omniagent"])


def main() -> None:
    """Main entry point for the API server."""
    import uvicorn
    
    uvicorn.run(
        "core.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )


if __name__ == "__main__":
    main()
