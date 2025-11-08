# 🤖 OmniCoreAgent Integration for Dprod

## Overview

Dprod now integrates **OmniCoreAgent**, a powerful AI development platform that provides:

- **🛠️ Local Tools System** - Custom Python functions as AI tools
- **🧠 Multi-Tier Memory** - Vector databases, Redis, PostgreSQL for learning
- **📡 Real-Time Events** - Live monitoring and streaming
- **🚁 Background Agents** - Autonomous task execution
- **🔧 Production-Ready** - Error handling, retry logic, observability

This integration replaces the placeholder AI implementation with real, production-ready AI capabilities.

---

## 🚀 Quick Start

### 1. Install OmniCoreAgent

```bash
cd /home/dev-soft/dprod
poetry add omnicoreagent
```

### 2. Configure Environment

Add to your `.env` file:

```bash
# Enable AI
AI_ENABLED=true
AI_FALLBACK_TO_RULES=true

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_openai_api_key_here

# Embedding for semantic memory
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# Memory & Events
OMNI_MEMORY_TYPE=redis
OMNI_EVENT_TYPE=redis_stream
```

### 3. Start the Services

```bash
# Start database and Redis
docker-compose up -d postgres redis

# Start API server
make dev-api
```

### 4. Test AI Integration

```bash
# Test with the existing test script
python scripts/test_ai_agent.py
```

---

## 🏗️ Architecture

### Integration Components

```
┌──────────────────────────────────────────────────────┐
│                  Dprod Platform                       │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │     OmniCoreAgent Integration Layer            │ │
│  │                                                 │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │  DprodOmniAgentService                   │ │ │
│  │  │  • Project analyzer agent                │ │ │
│  │  │  • Custom tool registry                  │ │ │
│  │  │  • Memory & event routers                │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  │                                                 │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │  DprodBackgroundAgents                   │ │ │
│  │  │  • Deployment health monitor             │ │ │
│  │  │  • Cost optimizer                        │ │ │
│  │  │  • Pattern learner                       │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  │                                                 │ │
│  │  ┌──────────────────────────────────────────┐ │ │
│  │  │  Custom AI Tools                         │ │ │
│  │  │  • analyze_project_structure             │ │ │
│  │  │  • detect_framework                      │ │ │
│  │  │  • read_config_files                     │ │ │
│  │  │  • suggest_build_config                  │ │ │
│  │  │  • validate_deployment_outcome           │ │ │
│  │  └──────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────┘ │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │     Existing Dprod Services                    │ │
│  │  • API Service (FastAPI)                       │ │
│  │  • Project Analyzer (now AI-powered)           │ │
│  │  • Detector (AI-enhanced)                      │ │
│  │  • Orchestrator (Docker)                       │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

### Files Created

1. **`services/ai/core/omnicore_service.py`**
   - Main OmniCoreAgent integration
   - Tool registry with dprod-specific tools
   - Agent creation and management
   - Response parsing

2. **`services/ai/core/background_agent_service.py`**
   - Background agent management
   - Autonomous monitoring agents
   - Cost optimization
   - Pattern learning

3. **`services/api/core/v1/routes/omniagent.py`**
   - REST API endpoints for OmniAgent
   - Project analysis endpoint
   - Background agent management
   - Agent control operations

4. **Updated `services/ai/core/project_analyzer_agent.py`**
   - Replaced placeholder AI with OmniCoreAgent
   - Fallback to rule-based when AI unavailable
   - Graceful error handling

---

## 📖 API Endpoints

### Project Analysis

**POST `/api/v1/omniagent/analyze`**

Analyze a project using AI:

```bash
curl -X POST http://localhost:8000/api/v1/omniagent/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "/path/to/project",
    "session_id": "optional-session-id"
  }'
```

Response:
```json
{
  "status": "success",
  "analysis": {
    "detected_framework": "nextjs",
    "confidence_score": 0.95,
    "project_type": "nodejs",
    "build_configuration": {...},
    "runtime_configuration": {...},
    "resource_requirements": {...},
    "detected_issues": [],
    "optimization_suggestions": [...]
  },
  "metadata": {
    "tokens_used": 1250,
    "cost_usd": 0.00187,
    "session_id": "abc-123"
  }
}
```

### Background Agents

**POST `/api/v1/omniagent/background-agents/create`**

Create autonomous background agent:

```bash
curl -X POST http://localhost:8000/api/v1/omniagent/background-agents/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "health_monitor"
  }'
```

Agent types:
- `health_monitor` - Check deployment health every 5 minutes
- `cost_optimizer` - Analyze costs hourly
- `pattern_learner` - Learn from patterns daily

**GET `/api/v1/omniagent/background-agents/list`**

List all background agents:

```bash
curl http://localhost:8000/api/v1/omniagent/background-agents/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**POST `/api/v1/omniagent/background-agents/control`**

Control agent operations:

```bash
curl -X POST http://localhost:8000/api/v1/omniagent/background-agents/control \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "deployment_health_monitor",
    "operation": "pause"
  }'
```

Operations: `pause`, `resume`, `stop`

**GET `/api/v1/omniagent/health`**

Check OmniCoreAgent installation status:

```bash
curl http://localhost:8000/api/v1/omniagent/health
```

---

## 🛠️ Custom Tools

The integration provides these AI tools:

### Project Analysis Tools

1. **`analyze_project_structure(project_path)`**
   - Scans directory structure
   - Identifies key files
   - Returns project layout

2. **`detect_framework(project_path)`**
   - Detects framework patterns
   - Returns detected frameworks with confidence

3. **`read_config_files(project_path, files)`**
   - Reads configuration files
   - Parses package.json, requirements.txt, etc.

4. **`suggest_build_config(project_analysis)`**
   - Suggests optimal build configuration
   - Returns build commands and steps

### Deployment Tools

5. **`get_deployment_status(deployment_id)`**
   - Gets deployment status from database

6. **`validate_deployment_outcome(deployment_id)`**
   - Validates deployment success
   - Records outcome for learning

7. **`analyze_resource_usage(deployment_id)`**
   - Analyzes resource consumption
   - Suggests optimizations

---

## 🚁 Background Agents

### Deployment Health Monitor

- **Interval**: Every 5 minutes
- **Purpose**: Monitor all active deployments
- **Actions**:
  - Check deployment URLs
  - Report unhealthy deployments
  - Analyze failure patterns
  - Suggest corrective actions

### Cost Optimizer

- **Interval**: Hourly
- **Purpose**: Optimize resource allocation
- **Actions**:
  - Analyze resource usage patterns
  - Identify over-provisioned deployments
  - Find idle deployments
  - Calculate cost savings

### Pattern Learner

- **Interval**: Daily
- **Purpose**: Continuous learning and improvement
- **Actions**:
  - Analyze successful deployments
  - Identify failure scenarios
  - Learn framework best practices
  - Update recommendations

---

## 🎯 Usage Examples

### Python Usage

```python
from services.ai.core.omnicore_service import DprodOmniAgentService
from services.api.core.db.database import get_db

async def analyze_project_example():
    """Example: Analyze a project with OmniCoreAgent."""
    async for db in get_db():
        service = DprodOmniAgentService(db)
        
        # Analyze project
        result = await service.analyze_project(
            project_path="/path/to/project",
            session_id="my-session"
        )
        
        # Parse result
        parsed = service.parse_omniagent_response(result)
        
        print(f"Framework: {parsed['detected_framework']}")
        print(f"Confidence: {parsed['confidence_score']}")
        print(f"Tokens: {parsed['tokens_used']}")
        print(f"Cost: ${parsed['cost_usd']}")
        
        break


async def create_background_agents():
    """Example: Create background agents."""
    from services.ai.core.background_agent_service import DprodBackgroundAgents
    
    async for db in get_db():
        bg_agents = DprodBackgroundAgents(db)
        
        # Create health monitor
        await bg_agents.create_deployment_monitor_agent()
        
        # Create cost optimizer
        await bg_agents.create_cost_optimizer_agent()
        
        # Create pattern learner
        await bg_agents.create_pattern_learner_agent()
        
        # List all agents
        agents = bg_agents.list_agents()
        print(f"Active agents: {agents}")
        
        break
```

---

## 🔧 Configuration Options

### LLM Providers

OmniCoreAgent supports multiple LLM providers:

```bash
# OpenAI (default)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini  # or gpt-4o, gpt-4-turbo
LLM_API_KEY=sk-...

# Anthropic Claude
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_KEY=sk-ant-...

# Groq (ultra-fast)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=gsk_...

# Local Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
# No API key needed
```

### Memory Backends

```bash
# In-memory (development)
OMNI_MEMORY_TYPE=in_memory

# Redis (recommended for production)
OMNI_MEMORY_TYPE=redis
REDIS_URL=redis://localhost:6379/0

# PostgreSQL
OMNI_MEMORY_TYPE=postgres
DATABASE_URL=postgresql://...

# MySQL
OMNI_MEMORY_TYPE=mysql

# SQLite
OMNI_MEMORY_TYPE=sqlite
```

### Vector Databases (Optional)

For semantic search and long-term memory:

```bash
# Qdrant
VECTOR_DB_TYPE=qdrant
QDRANT_URL=http://localhost:6333

# ChromaDB
VECTOR_DB_TYPE=chromadb
CHROMADB_PATH=/tmp/dprod/chromadb

# MongoDB
VECTOR_DB_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017
```

---

## 📊 Monitoring & Observability

### Token Usage Tracking

All AI operations track token usage and costs:

```sql
SELECT 
    agent_type,
    SUM(token_usage) as total_tokens,
    SUM(CAST(cost_estimate AS DECIMAL)) as total_cost,
    AVG(CAST(confidence_score AS DECIMAL)) as avg_confidence
FROM ai_agent_decisions
GROUP BY agent_type;
```

### AI Decision Accuracy

```sql
SELECT 
    COUNT(*) as total_decisions,
    SUM(CASE WHEN was_correct THEN 1 ELSE 0 END) as correct,
    AVG(CASE WHEN was_correct THEN 1.0 ELSE 0.0 END) as accuracy
FROM ai_agent_decisions
WHERE was_correct IS NOT NULL;
```

### Background Agent Status

```python
from services.ai.core.background_agent_service import DprodBackgroundAgents

bg_agents = DprodBackgroundAgents(db)

# List all agents
agents = bg_agents.list_agents()

# Get detailed status
for agent_id in agents:
    status = bg_agents.get_agent_status(agent_id)
    print(f"{agent_id}: {status}")
```

---

## 🐛 Troubleshooting

### OmniCoreAgent Not Installed

**Error**: `ImportError: No module named 'omnicoreagent'`

**Solution**:
```bash
poetry add omnicoreagent
# Or
pip install omnicoreagent
```

### AI Disabled

**Symptom**: Using rule-based analysis instead of AI

**Check**:
```bash
echo $AI_ENABLED  # Should be 'true'
echo $LLM_API_KEY  # Should be set
```

**Solution**:
```bash
export AI_ENABLED=true
export LLM_API_KEY=your_api_key
```

### Memory/Event Store Errors

**Error**: Redis connection failed

**Solution**:
```bash
# Start Redis
docker-compose up -d redis

# Or use in-memory for development
export OMNI_MEMORY_TYPE=in_memory
export OMNI_EVENT_TYPE=in_memory
```

### Background Agents Not Starting

**Check**:
```python
from services.ai.core.background_agent_service import DprodBackgroundAgents

bg_agents = DprodBackgroundAgents(db)
agents = bg_agents.list_agents()
print(agents)  # Should show agent IDs
```

**Solution**: Check logs for specific errors, ensure OmniCoreAgent is installed

---

## 🚀 Next Steps

1. **Install OmniCoreAgent**: `poetry add omnicoreagent`
2. **Configure API Keys**: Set `LLM_API_KEY` in `.env`
3. **Test Integration**: Run `python scripts/test_ai_agent.py`
4. **Create Background Agents**: Use API or Python
5. **Monitor Performance**: Check AI metrics in database
6. **Optimize Costs**: Review token usage and adjust

---

## 📚 Resources

- **OmniCoreAgent Documentation**: See `Omnicoreagent.md`
- **AI Integration Plan**: See `AIAgentIntegrationfoundationplan.md`
- **AI Agent README**: See `AI_AGENT_README.md`
- **API Documentation**: http://localhost:8000/docs

---

**Status**: ✅ Integration Complete - Ready for OmniCoreAgent Installation

**Installation**: `poetry add omnicoreagent`

**Configuration**: See `env.example` for all options
