"""AI Agent monitoring service for retrieving AI metrics and decision data."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.core.models import AIAgentDecision, AgentPerformance, ProjectPattern


class AIService:
    """Service for AI agent monitoring and metrics."""
    
    @staticmethod
    async def get_agent_decisions(
        db: AsyncSession,
        agent_type: Optional[str] = None,
        decision_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AIAgentDecision]:
        """Get paginated list of agent decisions."""
        query = select(AIAgentDecision)
        
        if agent_type:
            query = query.filter(AIAgentDecision.agent_type == agent_type)
        if decision_type:
            query = query.filter(AIAgentDecision.decision_type == decision_type)
            
        query = query.order_by(AIAgentDecision.timestamp.desc())
        query = query.limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_decision_by_id(
        db: AsyncSession,
        decision_id: str
    ) -> Optional[AIAgentDecision]:
        """Get a specific agent decision by ID."""
        query = select(AIAgentDecision).filter(AIAgentDecision.id == decision_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_agent_performance(
        db: AsyncSession,
        agent_type: Optional[str] = None,
        days: int = 30
    ) -> List[AgentPerformance]:
        """Get agent performance metrics over time."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(AgentPerformance).filter(
            AgentPerformance.date >= start_date
        )
        
        if agent_type:
            query = query.filter(AgentPerformance.agent_type == agent_type)
            
        query = query.order_by(AgentPerformance.date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_project_patterns(
        db: AsyncSession,
        pattern_type: Optional[str] = None,
        min_success_rate: float = 0.0
    ) -> List[ProjectPattern]:
        """Get learned project patterns."""
        query = select(ProjectPattern).filter(
            ProjectPattern.success_rate >= min_success_rate
        )
        
        if pattern_type:
            query = query.filter(ProjectPattern.pattern_type == pattern_type)
            
        query = query.order_by(ProjectPattern.success_rate.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_aggregated_metrics(
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get aggregated AI agent metrics."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total decisions
        total_decisions_query = select(func.count(AIAgentDecision.id)).filter(
            AIAgentDecision.timestamp >= start_date
        )
        total_decisions_result = await db.execute(total_decisions_query)
        total_decisions = total_decisions_result.scalar() or 0
        
        # Successful decisions (where is_correct = True)
        successful_query = select(func.count(AIAgentDecision.id)).filter(
            AIAgentDecision.timestamp >= start_date,
            AIAgentDecision.is_correct == True
        )
        successful_result = await db.execute(successful_query)
        total_successful = successful_result.scalar() or 0
        
        # Failed decisions (where is_correct = False)
        failed_query = select(func.count(AIAgentDecision.id)).filter(
            AIAgentDecision.timestamp >= start_date,
            AIAgentDecision.is_correct == False
        )
        failed_result = await db.execute(failed_query)
        total_failed = failed_result.scalar() or 0
        
        # Average confidence
        avg_confidence_query = select(func.avg(AIAgentDecision.confidence_score)).filter(
            AIAgentDecision.timestamp >= start_date
        )
        avg_confidence_result = await db.execute(avg_confidence_query)
        avg_confidence = avg_confidence_result.scalar() or 0.0
        
        # Total cost
        total_cost_query = select(func.sum(AIAgentDecision.cost_usd)).filter(
            AIAgentDecision.timestamp >= start_date
        )
        total_cost_result = await db.execute(total_cost_query)
        total_cost = total_cost_result.scalar() or 0.0
        
        # Decisions by type
        decisions_by_type_query = select(
            AIAgentDecision.decision_type,
            func.count(AIAgentDecision.id)
        ).filter(
            AIAgentDecision.timestamp >= start_date
        ).group_by(AIAgentDecision.decision_type)
        
        decisions_by_type_result = await db.execute(decisions_by_type_query)
        decisions_by_type = {
            decision_type: count 
            for decision_type, count in decisions_by_type_result.all()
        }
        
        # Performance trend (daily aggregation)
        performance_query = select(AgentPerformance).filter(
            AgentPerformance.date >= start_date
        ).order_by(AgentPerformance.date)
        
        performance_result = await db.execute(performance_query)
        performance_records = performance_result.scalars().all()
        
        performance_trend = [
            {
                'date': record.date.isoformat(),
                'total_decisions': record.total_decisions,
                'successful': record.successful_decisions,
                'failed': record.failed_decisions,
                'avg_confidence': record.avg_confidence,
                'cost': record.total_cost_usd
            }
            for record in performance_records
        ]
        
        success_rate = (total_successful / total_decisions * 100) if total_decisions > 0 else 0.0
        
        return {
            'total_decisions': total_decisions,
            'total_successful': total_successful,
            'total_failed': total_failed,
            'success_rate': success_rate,
            'avg_confidence': float(avg_confidence),
            'total_cost_usd': float(total_cost),
            'decisions_by_type': decisions_by_type,
            'performance_trend': performance_trend
        }
