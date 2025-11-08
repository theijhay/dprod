"""Background agents for autonomous dprod operations."""
from omnicoreagent.background_agent import BackgroundAgentService
from omnicoreagent.core.memory_store.memory_router import MemoryRouter
from omnicoreagent.core.events.event_router import EventRouter
from omnicoreagent.core.tools.local_tools_registry import ToolRegistry
import os
import json


class DprodBackgroundAgents:
    """
    Manage background agents for autonomous dprod operations.
    
    Background agents provide:
    - Deployment health monitoring
    - Cost optimization recommendations
    - Pattern learning and analysis
    - Performance monitoring
    """
    
    def __init__(self, db_session):
        """
        Initialize background agent service.
        
        Args:
            db_session: Database session for dprod operations
        """
        self.db_session = db_session
        self.bg_service = None
        self.memory_router = None
        self.event_router = None
        
        try:
            
            self.memory_router = MemoryRouter(
                memory_store_type=os.getenv("OMNI_MEMORY_TYPE", "in_memory")
            )
            self.event_router = EventRouter(
                event_store_type=os.getenv("OMNI_EVENT_TYPE", "in_memory")
            )
            self.bg_service = BackgroundAgentService(
                self.memory_router,
                self.event_router
            )
            self.bg_service.start_manager()
        except Exception as e:
            print(f"⚠️  Failed to initialize background agent service: {str(e)}")
    
    def _create_monitoring_tools(self):
        """Create tools for deployment monitoring."""
        tool_registry = ToolRegistry()
        
        @tool_registry.register_tool("check_all_deployments")
        def check_all_deployments() -> str:
            """Check health of all active deployments."""
            from services.shared.core.models import Deployment
            
            deployments = self.db_session.query(Deployment).filter_by(
                status="running"
            ).all()
            
            results = []
            for deployment in deployments:
                # Check deployment health
                try:
                    import requests
                    response = requests.get(deployment.url, timeout=5)
                    is_healthy = response.status_code == 200
                except:
                    is_healthy = False
                
                results.append({
                    "id": str(deployment.id),
                    "project_id": str(deployment.project_id),
                    "url": deployment.url,
                    "healthy": is_healthy,
                    "created_at": str(deployment.created_at)
                })
            
            return json.dumps({
                "total_deployments": len(results),
                "healthy_count": sum(1 for r in results if r['healthy']),
                "unhealthy_count": sum(1 for r in results if not r['healthy']),
                "deployments": results
            }, indent=2)
        
        @tool_registry.register_tool("get_deployment_metrics")
        def get_deployment_metrics() -> str:
            """Get overall deployment metrics."""
            from services.shared.core.models import Deployment, AIAgentDecision
            from sqlalchemy import func
            
            # Total deployments
            total = self.db_session.query(func.count(Deployment.id)).scalar()
            
            # Deployments by status
            status_counts = self.db_session.query(
                Deployment.status, 
                func.count(Deployment.id)
            ).group_by(Deployment.status).all()
            
            # AI decision accuracy
            ai_decisions = self.db_session.query(AIAgentDecision).filter(
                AIAgentDecision.was_correct.isnot(None)
            ).all()
            
            correct_decisions = sum(1 for d in ai_decisions if d.was_correct)
            accuracy = correct_decisions / len(ai_decisions) if ai_decisions else 0
            
            return json.dumps({
                "total_deployments": total,
                "status_breakdown": {status: count for status, count in status_counts},
                "ai_accuracy": f"{accuracy:.2%}",
                "ai_decisions_evaluated": len(ai_decisions)
            }, indent=2)
        
        return tool_registry
    
    async def create_deployment_monitor_agent(self):
        """Create agent to monitor deployment health."""
        if not self.bg_service:
            print("⚠️  Background agent service not available")
            return None
        
        tool_registry = self._create_monitoring_tools()
        if not tool_registry:
            return None
        
        agent_config = {
            "agent_id": "deployment_health_monitor",
            "system_instruction": """You are an autonomous deployment health monitor for dprod.
            
Your responsibilities:
1. Check all active deployments every 5 minutes
2. Identify unhealthy deployments
3. Analyze patterns in deployment failures
4. Suggest corrective actions
5. Track deployment success rates

Use the check_all_deployments and get_deployment_metrics tools to gather data.
Report any unhealthy deployments immediately with detailed analysis.""",
            "model_config": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": 0.2
            },
            "agent_config": {
                "max_steps": 10,
                "tool_call_timeout": 60
            },
            "interval": 300,  # 5 minutes in seconds
            "task_config": {
                "query": "Check all deployments and report any unhealthy ones. Analyze patterns and suggest fixes.",
                "schedule": "every 5 minutes",
                "interval": 300,
                "max_retries": 2,
                "retry_delay": 30
            },
            "local_tools": tool_registry
        }
        
        try:
            result = await self.bg_service.create(agent_config)
            print(f"✅ Deployment health monitor created: {result}")
            return result
        except Exception as e:
            print(f"⚠️  Failed to create deployment monitor: {str(e)}")
            return None
    
    async def create_cost_optimizer_agent(self):
        """Create agent to optimize deployment costs."""
        if not self.bg_service:
            print("⚠️  Background agent service not available")
            return None
        
        tool_registry = self._create_monitoring_tools()
        if not tool_registry:
            return None
        
        agent_config = {
            "agent_id": "cost_optimizer",
            "system_instruction": """You are a cost optimization agent for dprod.
            
Your responsibilities:
1. Analyze deployment resource usage patterns
2. Identify over-provisioned deployments
3. Suggest resource allocation optimizations
4. Find idle deployments that can be stopped
5. Calculate potential cost savings

Run hourly analysis and provide actionable recommendations.""",
            "model_config": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": 0.3
            },
            "agent_config": {
                "max_steps": 15,
                "tool_call_timeout": 90
            },
            "interval": 3600,  # 1 hour
            "task_config": {
                "query": "Analyze deployment costs and suggest optimizations. Identify over-provisioned resources.",
                "schedule": "every hour",
                "interval": 3600
            },
            "local_tools": tool_registry
        }
        
        try:
            result = await self.bg_service.create(agent_config)
            print(f"✅ Cost optimizer created: {result}")
            return result
        except Exception as e:
            print(f"⚠️  Failed to create cost optimizer: {str(e)}")
            return None
    
    async def create_pattern_learner_agent(self):
        """Create agent to learn from deployment patterns."""
        if not self.bg_service:
            print("⚠️  Background agent service not available")
            return None
        
        tool_registry = self._create_monitoring_tools()
        if not tool_registry:
            return None
        
        agent_config = {
            "agent_id": "pattern_learner",
            "system_instruction": """You are a pattern learning agent for dprod.
            
Your responsibilities:
1. Analyze successful deployment patterns
2. Identify common failure scenarios
3. Learn framework-specific best practices
4. Update deployment recommendations
5. Improve AI decision accuracy

Run daily analysis to continuously improve the system.""",
            "model_config": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": 0.4
            },
            "agent_config": {
                "max_steps": 20,
                "tool_call_timeout": 120
            },
            "interval": 86400,  # 24 hours (daily)
            "task_config": {
                "query": "Analyze deployment patterns from the last 24 hours. Learn from successes and failures.",
                "schedule": "daily",
                "interval": 86400
            },
            "local_tools": tool_registry
        }
        
        try:
            result = await self.bg_service.create(agent_config)
            print(f"✅ Pattern learner created: {result}")
            return result
        except Exception as e:
            print(f"⚠️  Failed to create pattern learner: {str(e)}")
            return None
    
    def list_agents(self):
        """List all background agents."""
        if not self.bg_service:
            return []
        return self.bg_service.list()
    
    def get_agent_status(self, agent_id: str):
        """Get status of a specific agent."""
        if not self.bg_service:
            return None
        return self.bg_service.get_agent_status(agent_id)
    
    def pause_agent(self, agent_id: str):
        """Pause a background agent."""
        if not self.bg_service:
            return False
        return self.bg_service.pause_agent(agent_id)
    
    def resume_agent(self, agent_id: str):
        """Resume a background agent."""
        if not self.bg_service:
            return False
        return self.bg_service.resume_agent(agent_id)
    
    def stop_agent(self, agent_id: str):
        """Stop a background agent."""
        if not self.bg_service:
            return False
        return self.bg_service.stop_agent(agent_id)
    
    def shutdown(self):
        """Shutdown all background agents."""
        if self.bg_service:
            self.bg_service.shutdown_manager()
            print("✅ Background agent manager shut down")
