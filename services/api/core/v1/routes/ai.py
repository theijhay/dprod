"""AI Agent monitoring endpoints."""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import get_db
from ..auth.dependencies import get_current_user
from ..schemas.ai_schema import (
    AgentDecisionResponse,
    AgentPerformanceResponse,
    ProjectPatternResponse,
    AgentMetricsResponse
)
from ..services.ai_service import AIService
from services.shared.core.models import User

router = APIRouter(prefix="/ai", tags=["AI Monitoring"])


@router.get("/metrics", response_model=AgentMetricsResponse)
async def get_ai_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated AI agent metrics and performance data."""
    metrics = await AIService.get_aggregated_metrics(db, days=days)
    return metrics


@router.get("/decisions", response_model=List[AgentDecisionResponse])
async def get_agent_decisions(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    decision_type: Optional[str] = Query(None, description="Filter by decision type"),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get paginated list of AI agent decisions."""
    decisions = await AIService.get_agent_decisions(
        db, 
        agent_type=agent_type,
        decision_type=decision_type,
        limit=limit,
        offset=offset
    )
    return decisions


@router.get("/decisions/{decision_id}", response_model=AgentDecisionResponse)
async def get_decision_details(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific AI agent decision."""
    decision = await AIService.get_decision_by_id(db, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.get("/performance", response_model=List[AgentPerformanceResponse])
async def get_agent_performance(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI agent performance metrics over time."""
    performance = await AIService.get_agent_performance(
        db,
        agent_type=agent_type,
        days=days
    )
    return performance


@router.get("/patterns", response_model=List[ProjectPatternResponse])
async def get_project_patterns(
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    min_success_rate: float = Query(0.0, ge=0.0, le=1.0, description="Minimum success rate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get learned project patterns and their success rates."""
    patterns = await AIService.get_project_patterns(
        db,
        pattern_type=pattern_type,
        min_success_rate=min_success_rate
    )
    return patterns
