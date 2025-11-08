#!/bin/bash
# OmniCoreAgent Installation Script for Dprod

echo "🤖 Installing OmniCoreAgent for Dprod"
echo "======================================"
echo ""

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install poetry first."
    echo "   Visit: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✅ Poetry found"
echo ""

echo "📦 Installing OmniCoreAgent and dependencies..."
echo "   This may take a few minutes due to dependency resolution..."
echo ""

# Install omnicoreagent with compatible dependencies
poetry add omnicoreagent \
    websockets@^15.0.1 \
    python-multipart@^0.0.20 \
    httpx@^0.27.0 \
    fastapi@^0.115.12 \
    uvicorn@^0.31.1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ OmniCoreAgent installed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Configure your .env file with API keys:"
    echo "      cp env.example .env"
    echo "      nano .env  # Add your LLM_API_KEY"
    echo ""
    echo "   2. Set required environment variables:"
    echo "      export AI_ENABLED=true"
    echo "      export LLM_API_KEY=your_openai_api_key_here"
    echo ""
    echo "   3. Start the services:"
    echo "      docker-compose up -d postgres redis"
    echo "      make dev-api"
    echo ""
    echo "   4. Test the integration:"
    echo "      python scripts/test_ai_agent.py"
    echo ""
    echo "📖 Full documentation: ./OMNICORE_INTEGRATION.md"
else
    echo ""
    echo "❌ Installation failed. Common issues:"
    echo "   1. Network timeout - Try again"
    echo "   2. Dependency conflicts - Check pyproject.toml"
    echo "   3. Python version - Ensure Python 3.10+"
    echo ""
    echo "💡 Manual installation:"
    echo "   poetry add omnicoreagent"
    exit 1
fi
poetry add omnicoreagent websockets@^15.0.1 python-multipart@^0.0.20 httpx@^0.27.0 fastapi@^0.115.12 uvicorn@^0.31.1