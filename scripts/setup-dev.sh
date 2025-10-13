#!/bin/bash

# Dprod Development Environment Setup Script

set -e

echo "🚀 Setting up Dprod development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p infrastructure/docker
mkdir -p infrastructure/kubernetes
mkdir -p infrastructure/terraform
mkdir -p infrastructure/scripts
mkdir -p docs/api
mkdir -p docs/architecture
mkdir -p docs/deployment
mkdir -p docs/user-guide
mkdir -p tests/e2e
mkdir -p tests/fixtures

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ Created .env file from template"
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if command -v poetry &> /dev/null; then
    poetry install
else
    echo "⚠️  Poetry not found. Installing via pip..."
    pip install -e .
fi

# Install Node.js dependencies for CLI
echo "📦 Installing Node.js dependencies..."
if [ -d "packages/cli" ]; then
    cd packages/cli
    if [ -f "package.json" ]; then
        npm install
    fi
    cd ../..
fi

# Install Node.js dependencies for Frontend
if [ -d "packages/frontend" ]; then
    cd packages/frontend
    if [ -f "package.json" ]; then
        npm install
    fi
    cd ../..
fi

# Start development environment
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
# TODO: Add migration commands here

echo "✅ Development environment setup complete!"
echo ""
echo "🎉 You can now start developing:"
echo "  • API Server: make dev-api"
echo "  • Full Stack: make dev"
echo "  • View API Docs: http://localhost:8000/docs"
echo "  • View Frontend: http://localhost:3000"
echo ""
echo "📚 Next steps:"
echo "  1. Create your first user: curl -X POST http://localhost:8000/auth/register"
echo "  2. Test the API: curl http://localhost:8000/health"
echo "  3. Start building features!"
