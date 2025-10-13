# 🚀 Dprod Quick Start Guide

Get Dprod up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (optional, for local development)
- Node.js 18+ (optional, for CLI development)

## Quick Setup

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd dprod
./scripts/setup-dev.sh
```

### 2. Start Development Environment
```bash
make dev
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- API server on port 8000
- CLI development environment

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 4. Install and Test CLI
```bash
# Install CLI dependencies
cd packages/cli
npm install

# Test CLI
node src/index.js --help

# Register a user (via API)
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Login with CLI (using the API key from registration)
node src/index.js login --token YOUR_API_KEY
```

### 5. Deploy Your First Project
```bash
# Create a simple Node.js project
mkdir test-app
cd test-app
echo '{"name":"test","version":"1.0.0","scripts":{"start":"node index.js"}}' > package.json
echo 'console.log("Hello from Dprod!");' > index.js

# Deploy it
node ../packages/cli/src/index.js deploy
```

## What You Get

✅ **Complete Backend Infrastructure**
- FastAPI server with authentication
- PostgreSQL database with migrations
- Redis for caching and sessions
- Docker container orchestration

✅ **Project Detection Engine**
- Automatically detects Node.js, Python, Go, Static sites
- Generates optimal deployment configurations
- Supports 20+ frameworks

✅ **CLI Tool**
- `dprod deploy` - Deploy any project
- `dprod login` - Authenticate
- `dprod status` - Check deployment status
- `dprod logs` - View deployment logs

✅ **Docker Orchestration**
- Automatic container creation and management
- Resource limits and cleanup
- Dynamic port mapping
- Health monitoring

## Development Commands

```bash
# Start all services
make dev

# Start individual services
make dev-api      # API server only
make dev-cli      # CLI development
make dev-frontend # Frontend (when implemented)

# Run tests
make test

# Code quality
make lint

# Clean up
make clean
```

## Project Structure

```
dprod/
├── packages/
│   ├── api/              # FastAPI backend
│   ├── orchestrator/     # Docker management
│   ├── detection-engine/ # Project detection
│   ├── cli/              # Command line tool
│   └── shared/           # Common types
├── infrastructure/       # Docker & deployment configs
├── docs/                # Documentation
└── scripts/             # Development scripts
```

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test Deployments**: Try deploying different project types
3. **Customize**: Modify detection rules or add new frameworks
4. **Scale**: Add more worker nodes or implement Kubernetes

## Troubleshooting

### Docker Issues
```bash
# Check Docker is running
docker ps

# Restart services
make clean && make dev
```

### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### CLI Issues
```bash
# Check API connection
curl http://localhost:8000/health

# Reinstall CLI dependencies
cd packages/cli && npm install
```

## Need Help?

- 📖 Check the full documentation in `docs/`
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

---

**Happy Deploying! 🎉**
