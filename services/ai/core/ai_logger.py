"""AI Logger for tracking agent decisions and performance."""

import json
import time
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.core.models import AIAgentDecision, AgentPerformance


class AILogger:
    """Logger for AI agent decisions and performance metrics."""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def log_agent_decision(
        self,
        agent_type: str,
        project_id: str,
        deployment_id: Optional[str],
        input_context: Dict[str, Any],
        tools_used: List[str],
        raw_response: str,
        parsed_decision: Dict[str, Any],
        confidence: float,
        processing_time: int,
        token_usage: int
    ) -> str:
        """
        Log comprehensive AI agent decision data.
        
        Returns:
            str: Decision ID
        """
        
        decision_record = AIAgentDecision(
            agent_type=agent_type,
            project_id=project_id,
            deployment_id=deployment_id,
            input_context=input_context,
            tools_used=tools_used if tools_used else None,
            raw_agent_response=str(parsed_decision),
            parsed_decision=parsed_decision,
            confidence_score=confidence, 
            processing_time_ms=processing_time,
            token_usage=token_usage,
            cost_estimate=self._calculate_cost(token_usage),
            decision_version='1.0.0'
        )
        
        self.db_session.add(decision_record)
        await self.db_session.commit()
        await self.db_session.refresh(decision_record)
        
        # Update real-time metrics
        await self._update_performance_metrics(agent_type, processing_time, token_usage)
        
        return str(decision_record.id)

    async def log_decision_verification(
        self,
        decision_id: str,
        was_correct: bool,
        verification_source: str,
        user_override: bool = False,
        override_reason: Optional[str] = None
    ):
        """Update decision with verification results."""
        
        # Get decision record
        decision = await self.db_session.get(AIAgentDecision, decision_id)
        if decision:
            decision.was_correct = was_correct  # Boolean
            decision.verification_source = verification_source
            decision.user_override = user_override  # Boolean
            decision.override_reason = override_reason
            decision.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            
            # Update pattern success rates if verified
            if verification_source == 'outcome':
                await self._update_pattern_success_rates(decision, was_correct)

    async def _update_performance_metrics(
        self,
        agent_type: str,
        processing_time: int,
        token_usage: int
    ):
        """Update real-time performance metrics."""
        
        today = datetime.utcnow().date()
        
        # Try to get existing record for today
        from sqlalchemy import select
        stmt = select(AgentPerformance).where(
            AgentPerformance.agent_type == agent_type,
            AgentPerformance.date == today
        )
        result = await self.db_session.execute(stmt)
        performance = result.scalar_one_or_none()
        
        if performance:
            # Update existing record
            performance.total_requests = performance.total_requests + 1
            performance.successful_requests = performance.successful_requests + 1
            performance.total_tokens_used = performance.total_tokens_used + token_usage
            performance.estimated_cost = (
                performance.estimated_cost + Decimal(str(self._calculate_cost(token_usage)))
            )
        else:
            # Create new record
            performance = AgentPerformance(
                agent_type=agent_type,
                date=today,
                total_requests=1,
                successful_requests=1,
                total_tokens_used=token_usage,
                estimated_cost=Decimal(str(self._calculate_cost(token_usage))),
                avg_processing_time_ms=processing_time
            )
            self.db_session.add(performance)
        
        await self.db_session.commit()

    async def _update_pattern_success_rates(
        self,
        decision: AIAgentDecision,
        was_correct: bool
    ):
        """Update pattern success rates based on decision outcomes."""
        # This will be implemented when we have project patterns
        pass

    def _calculate_cost(self, token_usage: int) -> float:
        """
        Calculate estimated cost based on token usage.
        Using GPT-4 pricing as reference: $0.03 per 1K tokens (input + output)
        """
        return (token_usage / 1000) * 0.03
