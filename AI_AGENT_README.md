# AI Agent Integration - Phase 1 Complete ✅

This document describes the AI agent foundation that has been integrated into dprod to create an intelligent, self-optimizing deployment platform.

## 🎯 Overview

The AI agent integration adds intelligent project analysis, decision tracking, and continuous learning capabilities to dprod. The system combines rule-based detection (fast, reliable) with AI-powered analysis (learns from every deployment).

## 🏗️ Architecture

### Components Implemented

1. **AI Logger** (`services/ai/core/ai_logger.py`)
   - Logs all AI agent decisions with full context
   - Tracks tokens used, cost, and confidence scores
   - Records deployment outcomes for learning
   - Maintains daily performance metrics

2. **Project Analyzer Agent** (`services/ai/core/project_analyzer_agent.py`)
   - AI-powered project type detection
   - Framework identification (Next.js, React, Django, Flask, etc.)
   - Build configuration suggestions
   - Supports both rule-based and AI analysis modes

3. **Project Analyzer Tools** (`services/ai/core/project_analyzer_tools.py`)
   - File structure analysis
   - Configuration file parsing
   - Framework pattern detection
   - Build configuration generation

4. **AI-Enhanced Detector** (`services/detector/core/ai_detector.py`)
   - Combines rule-based detection with AI verification
   - Compares traditional and AI-based results
   - Records deployment outcomes for continuous learning
   - Provides fallback to rule-based when AI unavailable

5. **AI Monitoring API** (`services/api/core/v1/routes/ai.py`)
   - `/api/v1/ai/metrics` - Aggregated performance metrics
   - `/api/v1/ai/decisions` - Paginated decision history
   - `/api/v1/ai/decisions/{id}` - Detailed decision info
   - `/api/v1/ai/performance` - Time-series performance data
   - `/api/v1/ai/patterns` - Learned project patterns

### Database Schema

Three new tables added via migration `076ae3b5902b`:

1. **ai_agent_decisions**
   - Stores every AI decision with full context
   - Includes input, output, tools used, confidence
   - Tracks tokens, cost, and execution time
   - Records verification (was the decision correct?)

2. **agent_performance**
   - Daily aggregated metrics per agent type
   - Success/failure counts
   - Average confidence and duration
   - Total tokens and costs

3. **project_patterns**
   - Learned patterns from successful deployments
   - Framework-specific indicators
   - Success rates and usage statistics
   - Average build times

## 🚀 Usage

### Running the AI-Enhanced Detector

```python
from pathlib import Path
from services.api.core.db.database import get_db
from services.detector.core.ai_detector import AIEnhancedDetector

async def detect_with_ai():
    async for db in get_db():
        detector = AIEnhancedDetector(db_session=db)
        
        result = await detector.detect_project(
            project_path=Path("/path/to/project"),
            project_id="my-project-123",
            deployment_id="deploy-456",
            use_ai=True  # Enable AI verification
        )
        
        # Deploy using recommended config
        config = result['recommended_config']
        
        # After deployment, record outcome
        await detector.verify_deployment_outcome(
            decision_id=result['decision_id'],
            was_successful=True,  # or False if failed
            feedback="Deployment completed successfully"
        )
        
        break
```

### Using Standalone AI Analyzer

```python
from services.ai.core.project_analyzer_agent import ProjectAnalyzerAgent

async def analyze_project():
    async for db in get_db():
        agent = ProjectAnalyzerAgent(db_session=db)
        
        result = await agent.analyze_project(
            project_path="/path/to/project",
            project_id="project-123",
            deployment_id="deploy-456"
        )
        
        print(f"Type: {result['project_type']}")
        print(f"Framework: {result['framework']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Build Config: {result['build_config']}")
        
        break
```

### Running the Test Suite

```bash
# Make sure API server is running
npm run dev:api

# In another terminal, run the AI agent test
cd /home/dev-soft/dprod
python scripts/test_ai_agent.py
```

The test will:
1. Analyze 3 example projects (Node.js, Python, Static)
2. Compare rule-based vs AI detection
3. Log all decisions to database
4. Record simulated deployment outcomes
5. Display summary with API endpoints

### Accessing AI Metrics

All endpoints require authentication (JWT token or API key):

```bash
# Get aggregated metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/ai/metrics?days=30

# Get recent decisions
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/ai/decisions?limit=10

# Get performance over time
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/ai/performance?days=7

# Get learned patterns
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/ai/patterns?min_success_rate=0.8
```

## 📊 What Gets Logged

Every AI decision logs:

- **Input Context**: Project path, files found, configurations
- **Tools Used**: Which analysis tools were invoked
- **Output**: Detected type, framework, build config
- **Confidence Score**: How certain the AI is (0.0 - 1.0)
- **Tokens Used**: For cost tracking
- **Cost**: Estimated in USD ($0.03 per 1K tokens)
- **Duration**: How long analysis took
- **Verification**: Whether deployment succeeded (updated after deployment)

## 🧠 Learning Mechanism

The system learns from deployment outcomes:

1. **Initial Detection**: AI analyzes project and logs decision
2. **Deployment**: Project is deployed using AI-suggested config
3. **Outcome Recording**: Success/failure is logged back to the decision
4. **Pattern Recognition**: Successful patterns are stored in `project_patterns`
5. **Performance Tracking**: Daily metrics updated in `agent_performance`
6. **Future Improvement**: AI uses learned patterns for better decisions

## 🎛️ Configuration

### AI Analysis Modes

The system supports three modes:

1. **Rule-based Only** (`use_ai=False`)
   - Fast, deterministic detection
   - No database logging
   - Good for development/testing

2. **AI-Enhanced** (`use_ai=True`, default)
   - Rule-based detection + AI verification
   - Logs all decisions
   - Learns from outcomes
   - Currently uses enhanced rule-based AI

3. **Full AI** (future)
   - Will use OpenAI/Claude/OmniCore APIs
   - Requires API keys in environment
   - Higher cost but more intelligent

### Cost Management

Current cost model:
- **Rule-based**: $0.00 (no AI API calls)
- **Enhanced Rule-based**: $0.00 (simulated AI)
- **Future OpenAI GPT-4**: ~$0.03 per 1K tokens

Set cost limits in environment:
```bash
# Maximum AI cost per month (USD)
AI_MONTHLY_BUDGET=50.00

# Enable/disable AI globally
AI_ENABLED=true
```

## 🔮 Future Enhancements

### Phase 2: AI Model Integration
- [ ] OpenAI GPT-4 integration
- [ ] Claude 3 integration
- [ ] OmniCore provider support
- [ ] Streaming responses for real-time feedback

### Phase 3: Advanced Learning
- [ ] Pattern clustering and analysis
- [ ] Automated A/B testing of configurations
- [ ] Confidence calibration
- [ ] Cost optimization strategies

### Phase 4: Predictive Features
- [ ] Build time prediction
- [ ] Failure probability estimation
- [ ] Resource requirement forecasting
- [ ] Optimization recommendations

## 📈 Monitoring Dashboard (Future)

Planned dashboard features:
- Real-time AI decision stream
- Cost tracking and budgets
- Success rate trends
- Most common failure patterns
- Framework distribution
- Confidence score distribution
- Token usage analytics

## 🔐 Security & Privacy

- All AI endpoints require authentication
- User data isolated by user ID
- No sensitive data sent to external AI APIs (yet)
- Decision logs can be purged after X days
- GDPR-compliant data retention policies

## 🤝 Contributing

To extend AI capabilities:

1. **Add New Detectors**: Extend `ProjectAnalyzerTools` with new analysis methods
2. **Add Frameworks**: Update `_rule_based_analyze()` with new framework patterns
3. **Improve Learning**: Enhance pattern recognition in `AILogger`
4. **Add AI Providers**: Create adapters in `ProjectAnalyzerAgent._ai_analyze()`

## 📝 Migration Guide

If you're upgrading from a previous version:

```bash
# Run the AI infrastructure migration
poetry run alembic upgrade head

# Verify tables were created
poetry run python -c "from services.api.core.db.database import engine; \
  import asyncio; \
  asyncio.run(engine.dispose())"

# Run test to populate initial data
python scripts/test_ai_agent.py
```

## 🐛 Troubleshooting

### Issue: AI endpoints return 401 Unauthorized
**Solution**: Make sure you're authenticated. Get a token:
```bash
dprod login
# Use the token from ~/.dprod/credentials.json
```

### Issue: Test script fails with database error
**Solution**: Make sure migrations are up to date:
```bash
poetry run alembic upgrade head
```

### Issue: No decisions showing in /ai/decisions
**Solution**: Run the test script to generate sample data:
```bash
python scripts/test_ai_agent.py
```

## 🤖 OmniCore Agent Integration Guide

### Overview

OmniCore is the recommended AI provider for dprod's intelligent deployment analysis. This section provides complete implementation, verification, and testing documentation.

### Current Status

**Phase 1**: ✅ Complete - Infrastructure ready (database, logging, monitoring)  
**Phase 2**: ⏳ Pending - OmniCore integration implementation  

The infrastructure is **fully prepared** for OmniCore integration. The `_ai_analyze()` method in `ProjectAnalyzerAgent` currently uses enhanced rule-based analysis as a placeholder.

### Implementation Steps

#### 1. Install Dependencies

```bash
cd /home/dev-soft/dprod
poetry add aiohttp python-dotenv
```

#### 2. Configure Environment Variables

Add to `.env` file:

```bash
# OmniCore Configuration
OMNICORE_API_KEY=your_api_key_here
OMNICORE_BASE_URL=https://api.omnicore.ai
OMNICORE_MODEL=omnicore-v1
OMNICORE_MAX_TOKENS=4000
OMNICORE_TEMPERATURE=0.1

# AI Feature Flags
AI_ENABLED=true
AI_PROVIDER=omnicore  # Options: omnicore, openai, claude
AI_MONTHLY_BUDGET=50.00
AI_FALLBACK_TO_RULES=true
```

#### 3. Create OmniCore Client

Create `services/ai/core/omnicore_client.py`:

```python
"""OmniCore AI Agent Client for intelligent project analysis."""

import os
import asyncio
from typing import Dict, Any, List, Optional
import aiohttp
from decimal import Decimal


class OmniCoreClient:
    """Client for OmniCore AI agent API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "omnicore-v1",
        max_tokens: int = 4000,
        temperature: float = 0.1
    ):
        self.api_key = api_key or os.getenv("OMNICORE_API_KEY")
        self.base_url = base_url or os.getenv("OMNICORE_BASE_URL", "https://api.omnicore.ai")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.session: Optional[aiohttp.ClientSession] = None
        
        if not self.api_key:
            raise ValueError("OMNICORE_API_KEY is required")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def analyze_project(
        self,
        project_context: Dict[str, Any],
        tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send project analysis request to OmniCore.
        
        Args:
            project_context: Project structure, configs, and patterns
            tools: Available analysis tools
            
        Returns:
            AI analysis result with framework detection and config
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Prepare system prompt
        system_prompt = self._get_system_prompt()
        
        # Prepare the payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._format_user_message(project_context)}
            ],
            "tools": tools,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OmniCore API error: {response.status} - {error_text}")
                
                result = await response.json()
                return self._parse_response(result)
                
        except asyncio.TimeoutError:
            raise Exception("OmniCore API request timed out")
        except Exception as e:
            raise Exception(f"OmniCore API error: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for project analysis."""
        return """You are an expert DevOps AI agent specialized in analyzing software projects 
and determining optimal deployment configurations.

Your task is to:
1. Analyze the project structure, files, and configuration
2. Identify the programming language, framework, and build tools
3. Determine the best deployment strategy (containerization, runtime, etc.)
4. Generate optimal build and runtime configurations
5. Provide confidence scores for your recommendations

Respond in JSON format with:
{
    "detected_framework": "framework_name",
    "confidence_score": 0.0-1.0,
    "project_type": "nodejs|python|go|static|etc",
    "build_configuration": [
        {"command": "...", "purpose": "..."}
    ],
    "runtime_configuration": {
        "start_command": "...",
        "expected_port": 3000,
        "environment_variables": {}
    },
    "resource_requirements": {
        "cpu": 0.5,
        "memory_mb": 512,
        "estimated_build_time": 120
    },
    "detected_issues": [],
    "optimization_suggestions": []
}

Be precise and confident in your analysis. Use the provided tools when needed."""
    
    def _format_user_message(self, context: Dict[str, Any]) -> str:
        """Format project context into user message."""
        import json
        return f"""Analyze this project:

Project Path: {context.get('project_path', 'unknown')}

Structure:
{json.dumps(context.get('structure', {}), indent=2)}

Configuration Files:
{json.dumps(context.get('config_files', {}), indent=2)}

Framework Patterns:
{json.dumps(context.get('framework_patterns', {}), indent=2)}

Please provide a comprehensive analysis with deployment recommendations."""
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OmniCore API response."""
        import json
        
        # Extract the assistant's message
        choices = response.get("choices", [])
        if not choices:
            raise Exception("No response from OmniCore")
        
        message = choices[0].get("message", {})
        content = message.get("content", "{}")
        
        # Parse JSON response
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError:
            # If not valid JSON, create fallback response
            analysis = {
                "detected_framework": "unknown",
                "confidence_score": 0.5,
                "project_type": "generic",
                "build_configuration": [],
                "runtime_configuration": {},
                "resource_requirements": {},
                "detected_issues": ["Failed to parse AI response"],
                "optimization_suggestions": []
            }
        
        # Extract usage stats
        usage = response.get("usage", {})
        analysis["tokens_used"] = usage.get("total_tokens", 0)
        analysis["cost_usd"] = self._calculate_cost(usage.get("total_tokens", 0))
        
        return analysis
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate estimated cost based on token usage."""
        # OmniCore pricing: $0.03 per 1K tokens (adjust as needed)
        return (tokens / 1000) * 0.03
```

#### 4. Update ProjectAnalyzerAgent

Modify `services/ai/core/project_analyzer_agent.py`:

```python
async def _ai_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use AI agent to analyze the project.
    Supports OmniCore, OpenAI, and Claude providers.
    """
    provider = os.getenv("AI_PROVIDER", "omnicore").lower()
    ai_enabled = os.getenv("AI_ENABLED", "false").lower() == "true"
    fallback_enabled = os.getenv("AI_FALLBACK_TO_RULES", "true").lower() == "true"
    
    if not ai_enabled:
        return await self._rule_based_analyze(context)
    
    try:
        if provider == "omnicore":
            from .omnicore_client import OmniCoreClient
            
            async with OmniCoreClient() as client:
                # Define available tools
                tools = self._get_analysis_tools()
                
                # Get AI analysis
                result = await client.analyze_project(context, tools)
                
                return result
        
        elif provider == "openai":
            # TODO: Implement OpenAI integration
            if fallback_enabled:
                return await self._rule_based_analyze(context)
            raise NotImplementedError("OpenAI integration pending")
        
        elif provider == "claude":
            # TODO: Implement Claude integration
            if fallback_enabled:
                return await self._rule_based_analyze(context)
            raise NotImplementedError("Claude integration pending")
        
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
    
    except Exception as e:
        print(f"⚠️  AI analysis failed: {str(e)}")
        if fallback_enabled:
            print("   Falling back to rule-based analysis")
            return await self._rule_based_analyze(context)
        raise

def _get_analysis_tools(self) -> List[Dict[str, Any]]:
    """Define tools available to the AI agent."""
    return [
        {
            "type": "function",
            "function": {
                "name": "analyze_project_structure",
                "description": "Get detailed project structure analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "scan_depth": {
                            "type": "integer",
                            "description": "Directory scan depth",
                            "default": 2
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_framework_patterns",
                "description": "Detect framework-specific patterns in the project",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]
```

### Verification & Testing

#### 1. Unit Tests

Create `services/ai/tests/test_omnicore_client.py`:

```python
"""Tests for OmniCore client."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from services.ai.core.omnicore_client import OmniCoreClient


@pytest.mark.asyncio
async def test_omnicore_client_initialization():
    """Test client initialization with API key."""
    with patch.dict('os.environ', {'OMNICORE_API_KEY': 'test-key'}):
        client = OmniCoreClient()
        assert client.api_key == 'test-key'
        assert client.model == 'omnicore-v1'


@pytest.mark.asyncio
async def test_omnicore_client_missing_api_key():
    """Test client fails without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="OMNICORE_API_KEY is required"):
            OmniCoreClient()


@pytest.mark.asyncio
async def test_analyze_project_success():
    """Test successful project analysis."""
    mock_response = {
        "choices": [{
            "message": {
                "content": '{"detected_framework": "nextjs", "confidence_score": 0.95}'
            }
        }],
        "usage": {"total_tokens": 1500}
    }
    
    with patch.dict('os.environ', {'OMNICORE_API_KEY': 'test-key'}):
        client = OmniCoreClient()
        
        # Mock the HTTP session
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.json = AsyncMock(return_value=mock_response)
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response_obj
            
            context = {"project_path": "/test"}
            result = await client.analyze_project(context, [])
            
            assert result["detected_framework"] == "nextjs"
            assert result["confidence_score"] == 0.95
            assert result["tokens_used"] == 1500


@pytest.mark.asyncio
async def test_analyze_project_api_error():
    """Test handling of API errors."""
    with patch.dict('os.environ', {'OMNICORE_API_KEY': 'test-key'}):
        client = OmniCoreClient()
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 500
            mock_response_obj.text = AsyncMock(return_value="Server error")
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response_obj
            
            context = {"project_path": "/test"}
            
            with pytest.raises(Exception, match="OmniCore API error"):
                await client.analyze_project(context, [])


@pytest.mark.asyncio
async def test_cost_calculation():
    """Test token cost calculation."""
    with patch.dict('os.environ', {'OMNICORE_API_KEY': 'test-key'}):
        client = OmniCoreClient()
        
        # 1000 tokens at $0.03 per 1K = $0.03
        cost = client._calculate_cost(1000)
        assert cost == 0.03
        
        # 2500 tokens at $0.03 per 1K = $0.075
        cost = client._calculate_cost(2500)
        assert cost == 0.075
```

#### 2. Integration Tests

Create `scripts/test_omnicore_integration.py`:

```python
"""Integration test for OmniCore AI agent."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api.core.db.database import get_db
from services.ai.core.project_analyzer_agent import ProjectAnalyzerAgent


async def test_omnicore_integration():
    """Test complete OmniCore integration."""
    
    print("=" * 80)
    print("🤖 OMNICORE INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Check environment
    api_key = os.getenv("OMNICORE_API_KEY")
    if not api_key:
        print("❌ OMNICORE_API_KEY not set")
        print("   Set it in .env file or export OMNICORE_API_KEY=your_key")
        return False
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    print(f"✅ Provider: {os.getenv('AI_PROVIDER', 'omnicore')}")
    print(f"✅ AI Enabled: {os.getenv('AI_ENABLED', 'false')}")
    print()
    
    # Test with real project
    test_projects = [
        "/home/dev-soft/dprod/examples/nodejs",
        "/home/dev-soft/dprod/examples/python",
        "/home/dev-soft/dprod/tools/frontend"
    ]
    
    async for db in get_db():
        agent = ProjectAnalyzerAgent(db_session=db)
        
        for project_path in test_projects:
            if not Path(project_path).exists():
                print(f"⚠️  Skipping {project_path} (not found)")
                continue
            
            print(f"\n{'=' * 80}")
            print(f"Testing: {project_path}")
            print(f"{'=' * 80}")
            
            try:
                result = await agent.analyze_project(
                    project_path=project_path,
                    project_id=None,
                    deployment_id=None
                )
                
                print(f"✅ Analysis complete!")
                print(f"   Framework: {result.get('framework', 'unknown')}")
                print(f"   Confidence: {result.get('confidence', 0):.2%}")
                print(f"   Tokens: {result.get('tokens_used', 0)}")
                print(f"   Cost: ${result.get('cost_usd', 0):.6f}")
                
                if result.get('build_config'):
                    print(f"   Build steps: {len(result['build_config'].get('build_steps', []))}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        break
    
    print(f"\n{'=' * 80}")
    print("Test complete!")
    print(f"{'=' * 80}")
    return True


if __name__ == "__main__":
    asyncio.run(test_omnicore_integration())
```

Run the integration test:

```bash
# Set your OmniCore API key
export OMNICORE_API_KEY=your_actual_api_key
export AI_ENABLED=true
export AI_PROVIDER=omnicore

# Run the test
python scripts/test_omnicore_integration.py
```

#### 3. Performance Testing

Create `scripts/test_omnicore_performance.py`:

```python
"""Performance and load testing for OmniCore integration."""

import asyncio
import time
from statistics import mean, median, stdev

async def test_performance():
    """Test OmniCore performance metrics."""
    
    results = {
        "response_times": [],
        "token_usage": [],
        "costs": [],
        "confidence_scores": []
    }
    
    # Run 10 analyses
    for i in range(10):
        start = time.time()
        
        # Your analysis code here
        
        duration = time.time() - start
        results["response_times"].append(duration)
    
    print(f"Performance Results:")
    print(f"  Average response time: {mean(results['response_times']):.2f}s")
    print(f"  Median response time: {median(results['response_times']):.2f}s")
    print(f"  Std deviation: {stdev(results['response_times']):.2f}s")
    print(f"  Average tokens: {mean(results['token_usage']):.0f}")
    print(f"  Average cost: ${mean(results['costs']):.6f}")
```

### Cost Monitoring

Monitor AI costs in the database:

```sql
-- Total cost by day
SELECT 
    DATE(created_at) as date,
    SUM(CAST(cost_estimate AS DECIMAL)) as daily_cost,
    COUNT(*) as decisions
FROM ai_agent_decisions
WHERE agent_type = 'project_analyzer'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Cost by project (if project_id is set)
SELECT 
    project_id,
    SUM(CAST(cost_estimate AS DECIMAL)) as total_cost,
    AVG(CAST(confidence_score AS DECIMAL)) as avg_confidence
FROM ai_agent_decisions
WHERE project_id IS NOT NULL
GROUP BY project_id;
```

### Troubleshooting

**Issue**: `OMNICORE_API_KEY is required`  
**Solution**: Set the environment variable in `.env`

**Issue**: Connection timeout  
**Solution**: Check network connectivity and API status

**Issue**: High costs  
**Solution**: Review `AI_MONTHLY_BUDGET` and enable `AI_FALLBACK_TO_RULES`

**Issue**: Low confidence scores  
**Solution**: Provide more context in project analysis

### Migration from Rule-Based to AI

Gradual rollout strategy:

1. **Week 1-2**: Run AI in parallel, log both results
2. **Week 3**: Enable AI for 25% of projects (A/B test)
3. **Week 4**: Review accuracy, adjust to 50%
4. **Week 5**: Scale to 100% with fallback enabled

## 📚 References

- [AI Integration Plan](./AIAgentIntegrationfoundationplan.md) - Complete implementation plan
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Database Models](./services/shared/core/models.py) - SQLAlchemy models
- [Migration](./alembic/versions/076ae3b5902b_add_ai_agent_infrastructure.py) - Database schema

---

**Status**: ✅ Phase 1 Complete | ⏳ Phase 2 (OmniCore) Ready for Implementation  
**Next Steps**: Obtain OmniCore API key, implement client, run integration tests
