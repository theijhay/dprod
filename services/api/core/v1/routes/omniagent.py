"""OmniAgent API endpoints for dprod."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.core.db.database import get_db
from services.api.core.v1.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional
import omnicoreagent

router = APIRouter(prefix="/omniagent", tags=["OmniAgent"])


class AnalyzeProjectRequest(BaseModel):
    """Request model for project analysis."""
    project_path: str
    session_id: Optional[str] = None


class BackgroundAgentRequest(BaseModel):
    """Request model for background agent creation."""
    agent_type: str  # "health_monitor", "cost_optimizer", "pattern_learner"


class AgentControlRequest(BaseModel):
    """Request model for agent control operations."""
    agent_id: str
    operation: str  # "pause", "resume", "stop"


@router.post("/analyze")
async def analyze_project_with_omni(
    request: AnalyzeProjectRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze project using OmniCoreAgent.
    
    Returns intelligent project analysis with framework detection,
    build configuration, and optimization recommendations.
    """
    try:
        from services.ai.core.omnicore_service import DprodOmniAgentService
        
        service = DprodOmniAgentService(db)
        result = await service.analyze_project(
            project_path=request.project_path,
            session_id=request.session_id
        )
        
        # Parse the result
        parsed = service.parse_omniagent_response(result)
        
        return {
            "status": "success",
            "analysis": parsed,
            "metadata": {
                "tokens_used": result.get("total_tokens", 0),
                "cost_usd": result.get("total_cost", 0.0),
                "session_id": request.session_id
            }
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OmniCoreAgent not installed. Install with: poetry add omnicoreagent"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/background-agents/create")
async def create_background_agent(
    request: BackgroundAgentRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a background agent for autonomous operations.
    
    Available agent types:
    - health_monitor: Monitor deployment health (every 5 minutes)
    - cost_optimizer: Analyze and optimize costs (hourly)
    - pattern_learner: Learn from deployment patterns (daily)
    """
    try:
        from services.ai.core.background_agent_service import DprodBackgroundAgents
        
        bg_agents = DprodBackgroundAgents(db)
        
        if request.agent_type == "health_monitor":
            result = await bg_agents.create_deployment_monitor_agent()
        elif request.agent_type == "cost_optimizer":
            result = await bg_agents.create_cost_optimizer_agent()
        elif request.agent_type == "pattern_learner":
            result = await bg_agents.create_pattern_learner_agent()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent type: {request.agent_type}. "
                       f"Valid types: health_monitor, cost_optimizer, pattern_learner"
            )
        
        if not result:
            raise HTTPException(
                status_code=503,
                detail="Failed to create background agent. Check logs for details."
            )
        
        return {
            "status": "success",
            "agent_type": request.agent_type,
            "agent": result
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OmniCoreAgent not installed. Install with: poetry add omnicoreagent"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create background agent: {str(e)}"
        )


@router.get("/background-agents/list")
async def list_background_agents(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active background agents."""
    try:
        from services.ai.core.background_agent_service import DprodBackgroundAgents
        
        bg_agents = DprodBackgroundAgents(db)
        agents = bg_agents.list_agents()
        
        # Get detailed status for each agent
        agent_details = []
        for agent_id in agents:
            status = bg_agents.get_agent_status(agent_id)
            if status:
                agent_details.append(status)
        
        return {
            "status": "success",
            "total_agents": len(agents),
            "agents": agent_details
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OmniCoreAgent not installed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/background-agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed status of a specific background agent."""
    try:
        from services.ai.core.background_agent_service import DprodBackgroundAgents
        
        bg_agents = DprodBackgroundAgents(db)
        status = bg_agents.get_agent_status(agent_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Agent not found: {agent_id}"
            )
        
        return {
            "status": "success",
            "agent": status
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OmniCoreAgent not installed"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.post("/background-agents/control")
async def control_background_agent(
    request: AgentControlRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Control background agent operations.
    
    Operations:
    - pause: Temporarily pause agent execution
    - resume: Resume a paused agent
    - stop: Stop agent permanently
    """
    try:
        from services.ai.core.background_agent_service import DprodBackgroundAgents
        
        bg_agents = DprodBackgroundAgents(db)
        
        if request.operation == "pause":
            success = bg_agents.pause_agent(request.agent_id)
            message = "Agent paused"
        elif request.operation == "resume":
            success = bg_agents.resume_agent(request.agent_id)
            message = "Agent resumed"
        elif request.operation == "stop":
            success = bg_agents.stop_agent(request.agent_id)
            message = "Agent stopped"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation: {request.operation}. "
                       f"Valid operations: pause, resume, stop"
            )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to {request.operation} agent: {request.agent_id}"
            )
        
        return {
            "status": "success",
            "agent_id": request.agent_id,
            "operation": request.operation,
            "message": message
        }
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="OmniCoreAgent not installed"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to control agent: {str(e)}"
        )


@router.get("/health")
async def omniagent_health():
    """Check if OmniCoreAgent is installed and available."""
    try:
        version = getattr(omnicoreagent, '__version__', 'unknown')
        return {
            "status": "healthy",
            "omnicoreagent_installed": True,
            "version": version
        }
    except ImportError:
        return {
            "status": "unavailable",
            "omnicoreagent_installed": False,
            "message": "Install with: poetry add omnicoreagent"
        }
