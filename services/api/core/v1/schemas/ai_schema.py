"""AI Agent monitoring schemas."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentDecisionResponse(BaseModel):
    """Response model for agent decision."""
    id: str
    agent_type: str
    decision_type: str
    input_context: Dict[str, Any]
    output_response: Dict[str, Any]
    tools_used: List[str]
    confidence_score: float
    tokens_used: int
    cost_usd: float
    duration_seconds: float
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AgentPerformanceResponse(BaseModel):
    """Response model for agent performance metrics."""
    id: str
    agent_type: str
    date: datetime
    total_decisions: int
    successful_decisions: int
    failed_decisions: int
    avg_confidence: float
    avg_duration: float
    total_tokens_used: int
    total_cost_usd: float
    
    class Config:
        from_attributes = True


class ProjectPatternResponse(BaseModel):
    """Response model for project pattern."""
    id: str
    pattern_type: str
    pattern_name: str
    indicators: Dict[str, Any]
    success_rate: float
    usage_count: int
    avg_build_time: Optional[float] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AgentMetricsResponse(BaseModel):
    """Response model for aggregated agent metrics."""
    total_decisions: int
    total_successful: int
    total_failed: int
    success_rate: float
    avg_confidence: float
    total_cost_usd: float
    decisions_by_type: Dict[str, int]
    performance_trend: List[Dict[str, Any]]
