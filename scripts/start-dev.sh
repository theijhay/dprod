#!/bin/bash
# Dprod Development Startup Script
# This script starts all required services for local development

echo "======================================================================="
echo "🚀 Dprod Development Environment Setup"
echo "======================================================================="

# Check if we're in the dprod directory
if [ ! -f "package.json" ] || [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the dprod root directory"
    exit 1
fi

echo ""
echo "Step 1: Starting Docker services (PostgreSQL + Redis)..."
echo "-----------------------------------------------------------------------"
docker-compose up -d postgres redis

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ PostgreSQL failed to start"
    docker-compose logs postgres
    exit 1
fi

if ! docker-compose ps redis | grep -q "Up"; then
    echo "❌ Redis failed to start"
    docker-compose logs redis
    exit 1
fi

echo "✅ Docker services running"

echo ""
echo "Step 2: Running database migrations..."
echo "-----------------------------------------------------------------------"
poetry run alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Database migrations failed"
    exit 1
fi

echo "✅ Database is ready"

echo ""
echo "Step 3: Checking Python dependencies..."
echo "-----------------------------------------------------------------------"
if ! poetry show omnicoreagent > /dev/null 2>&1; then
    echo "⚠️  OmniCoreAgent not installed, installing..."
    poetry add omnicoreagent
else
    echo "✅ OmniCoreAgent is installed"
fi

echo ""
echo "Step 4: Setting up environment..."
echo "-----------------------------------------------------------------------"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found, creating from env.example..."
    cp env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "💡 To enable AI features, edit .env and set:"
    echo "   AI_ENABLED=true"
    echo "   LLM_API_KEY=your-openai-api-key"
else
    echo "✅ .env file exists"
fi

echo ""
echo "======================================================================="
echo "✅ Setup Complete! Ready to start development"
echo "======================================================================="
echo ""
echo "🎯 Choose how to run Dprod:"
echo ""
echo "Option 1: Local Development (Recommended)"
echo "   npm run dev              - Start API + CLI"
echo "   make dev                 - Same as above"
echo ""
echo "Option 2: Full Docker (All services in containers)"
echo "   docker-compose up        - Start all services in Docker"
echo ""
echo "Option 3: API Only"
echo "   npm run dev:api          - Start only the API server"
echo "   make dev-api             - Same as above"
echo ""
echo "-----------------------------------------------------------------------"
echo "📊 Service Status:"
echo "-----------------------------------------------------------------------"
docker-compose ps

echo ""
echo "-----------------------------------------------------------------------"
echo "📚 Useful Commands:"
echo "-----------------------------------------------------------------------"
echo "   docker-compose logs -f   - View all Docker logs"
echo "   docker-compose down      - Stop all Docker services"
echo "   make help                - Show all available commands"
echo "   python scripts/test_ai_integration.py - Test AI integration"
echo "   python scripts/test_deployment_flow.py - Test Docker stats"
echo ""
echo "🌐 Services will be available at:"
echo "   API:        http://localhost:8000"
echo "   API Docs:   http://localhost:8000/docs"
echo "   PostgreSQL: localhost:5432"
echo "   Redis:      localhost:6379"
echo ""
echo "======================================================================="
