# 📚 Dprod Documentation

> **Zero-configuration deployment platform** - Deploy any project with a single command, regardless of technology stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

---

## 📋 Table of Contents

1. [🎯 Overview](#-overview)
2. [🏗️ Architecture](#️-architecture)
3. [📁 Project Structure](#-project-structure)
4. [🚀 Quick Start](#-quick-start)
5. [🛠️ Development](#️-development)
6. [🔧 Configuration](#-configuration)
7. [📦 API Reference](#-api-reference)
8. [💻 CLI Reference](#-cli-reference)
9. [🐳 Docker & Deployment](#-docker--deployment)
10. [🧪 Testing](#-testing)
11. [📈 Examples](#-examples)
12. [🔍 Troubleshooting](#-troubleshooting)
13. [🤝 Contributing](#-contributing)

---

## 🎯 Overview

### What is Dprod?

Dprod is a **zero-configuration deployment platform** that allows developers to deploy ANY project with a single command, regardless of the technology stack, without any configuration files or setup.

### The Problem We Solve

- Developers waste hours configuring deployment environments
- Writing Dockerfiles, setting up CI/CD, managing infrastructure
- Most deployment solutions require significant configuration and platform-specific knowledge
- What takes 5 minutes to run locally takes 5+ hours to deploy properly

### The Solution

```bash
cd /your/project
dprod deploy
# → 🔍 Analyzing your project...
# → 📦 Packaging your code...
# → 🚀 Deploying to the cloud...
# → ✅ Success! Your app is live at: https://your-project-abc123.dprod.app
```

### ✅ Current Status

**Fully Working Features:**
- ✅ **CLI Tool**: Published to npm as `dprod-cli`
- ✅ **API Server**: Complete with authentication and project management
- ✅ **Project Detection**: Automatically detects Node.js, Python, Go, and Static projects
- ✅ **Docker Integration**: Builds and runs containers automatically
- ✅ **URL Generation**: Free tier with `*.dprod.app` subdomains
- ✅ **Real-time Logs**: Live deployment progress streaming
- ✅ **Database**: PostgreSQL with user and project management
- ✅ **Authentication**: Email-based login with API keys

**Ready for Production:**
- 🚀 **Deploy any Node.js project** with `dprod deploy`
- 🚀 **Get instant URLs** - no configuration needed
- 🚀 **Real-time monitoring** with live logs
- 🚀 **Zero setup** - works out of the box

**No configuration files. No server setup. No infrastructure knowledge required.**

### Key Features

- ✅ **Universal Project Detection** - Automatically detects Node.js, Python, Go, Static sites
- ✅ **Zero Configuration** - No Dockerfiles, config files, or setup required
- ✅ **Real-time Logs** - Stream deployment progress in real-time
- ✅ **Auto SSL** - Automatic HTTPS with custom subdomains
- ✅ **Resource Management** - Automatic container limits and cleanup
- ✅ **CLI Tool** - Beautiful command-line interface
- ✅ **Web Dashboard** - Monitor deployments (coming soon)

---

## 🏗️ Architecture

### Dprod Platform Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DPROD PLATFORM                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                           CORE SERVICES                                │    │
│  │                                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │   API       │  │ Detection   │  │Orchestrator │  │   Reverse   │    │    │
│  │  │  Server     │  │  Engine     │  │   Service   │  │   Proxy     │    │    │
│  │  │ (FastAPI)   │  │ (Python)    │  │ (Python)    │  │ (Traefik)   │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  │                                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │ PostgreSQL  │  │    Redis    │  │   Docker    │  │   File      │    │    │
│  │  │ (Database)  │  │  (Cache)    │  │  Engine     │  │  Storage    │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        USER INTERFACES                                 │    │
│  │                                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │   CLI       │  │  Web        │  │   Mobile    │  │   API       │    │    │
│  │  │  Tool       │  │ Dashboard   │  │     App     │  │  Gateway    │    │    │
│  │  │ (Node.js)   │  │ (React)     │  │  (Future)   │  │ (Future)    │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        DEPLOYMENT LAYER                                │    │
│  │                                                                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │    │
│  │  │   User      │  │   User      │  │   User      │  │   User      │    │    │
│  │  │   App 1     │  │   App 2     │  │   App 3     │  │   App N     │    │    │
│  │  │ (Container) │  │ (Container) │  │ (Container) │  │ (Container) │    │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Core Components

#### **1. API Server** (FastAPI)
- **Purpose**: Central hub for all platform operations
- **Responsibilities**:
  - User authentication and authorization
  - Project management (create, read, update, delete)
  - Deployment orchestration
  - Real-time status updates
  - WebSocket connections for live logs
- **Port**: 8000
- **Technology**: Python 3.11+, FastAPI, SQLAlchemy

#### **2. Detection Engine** (Python)
- **Purpose**: Automatically detect project types and generate configurations
- **Responsibilities**:
  - Scan project directories for framework indicators
  - Generate appropriate Dockerfiles
  - Create deployment configurations
  - Support multiple languages (Node.js, Python, Go, Static)
- **Technology**: Python 3.11+, Pathlib, Jinja2

#### **3. Orchestrator Service** (Python)
- **Purpose**: Manage Docker containers and deployment lifecycle
- **Responsibilities**:
  - Build Docker images from project code
  - Run and manage containers
  - Handle resource allocation and limits
  - Monitor container health
  - Clean up old deployments
- **Technology**: Python 3.11+, Docker SDK, asyncio

#### **4. Reverse Proxy** (Traefik)
- **Purpose**: Route traffic to deployed applications
- **Responsibilities**:
  - Dynamic subdomain routing
  - SSL certificate management
  - Load balancing
  - Health checks
- **Technology**: Traefik, Let's Encrypt

#### **5. Database** (PostgreSQL)
- **Purpose**: Persistent data storage
- **Responsibilities**:
  - User accounts and authentication
  - Project metadata and configurations
  - Deployment history and logs
  - System settings and preferences
- **Technology**: PostgreSQL 15+, SQLAlchemy ORM

#### **6. Cache** (Redis)
- **Purpose**: High-performance caching and session management
- **Responsibilities**:
  - User session storage
  - API response caching
  - Job queue management
  - Real-time data storage
- **Technology**: Redis 7+, aioredis

#### **7. File Storage** (Local/Cloud)
- **Purpose**: Store project source code and build artifacts
- **Responsibilities**:
  - Project source code archives
  - Docker build contexts
  - Deployment artifacts
  - Log files and backups
- **Technology**: Local filesystem (dev), S3/MinIO (production)

### User Interfaces

#### **1. CLI Tool** (Node.js)
- **Purpose**: Command-line interface for developers
- **Commands**: `deploy`, `login`, `status`, `logs`, `list`
- **Technology**: Node.js 18+, Commander.js, Axios

#### **2. Web Dashboard** (React)
- **Purpose**: Web-based management interface
- **Features**: Project management, deployment monitoring, logs viewer
- **Technology**: React 18+, Next.js, TypeScript

#### **3. API Gateway** (Future)
- **Purpose**: External API access for integrations
- **Features**: RESTful API, webhooks, third-party integrations
- **Technology**: FastAPI, OpenAPI 3.0

### Deployment Layer

#### **User Applications**
- **Purpose**: Host user-deployed applications
- **Technology**: Docker containers
- **Features**:
  - Automatic subdomain assignment
  - SSL certificate provisioning
  - Health monitoring
  - Resource limits and scaling
  - Automatic cleanup

### Data Flow

```
1. User runs `dprod deploy` → CLI Tool
2. CLI authenticates → API Server
3. CLI uploads project → File Storage
4. API triggers detection → Detection Engine
5. Detection generates config → API Server
6. API triggers deployment → Orchestrator Service
7. Orchestrator builds image → Docker Engine
8. Orchestrator runs container → Docker Engine
9. Reverse Proxy routes traffic → User Application
10. User accesses app → https://app-name.dprod.app
```

### Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, asyncio
- **Database**: PostgreSQL 15+, Redis 7+
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Traefik
- **CLI**: Node.js 18+, Commander.js
- **Frontend**: React 18+, Next.js, TypeScript
- **Infrastructure**: Docker Compose (dev), Kubernetes (production)

---

## 📁 Project Structure

```
dprod/
├── services/                   # Backend services (production)
│   ├── api/                    # FastAPI backend service
│   │   ├── core/               # Main business logic
│   │   │   ├── v1/             # API version 1
│   │   │   │   ├── auth/       # Authentication
│   │   │   │   ├── routes/     # API endpoints
│   │   │   │   └── services/   # Business services
│   │   │   ├── db/             # Database layer
│   │   │   └── utils/          # Utilities
│   │   ├── tests/              # API tests
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── orchestrator/           # Deployment orchestration
│   │   ├── core/               # Orchestration logic
│   │   │   ├── docker/         # Docker management
│   │   │   ├── deployment/     # Deployment logic
│   │   │   └── monitoring/     # Health checks
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── detector/               # Project detection
│   │   ├── core/               # Detection logic
│   │   │   ├── detectors/      # Framework detectors
│   │   │   ├── config/         # Configuration generators
│   │   │   └── templates/      # Dockerfile templates
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   └── shared/                 # Shared types & utilities
│       ├── core/               # Shared code
│       │   ├── types/          # TypeScript/Python types
│       │   ├── constants/      # Shared constants
│       │   └── utils/          # Common utilities
│       ├── pyproject.toml
│       └── package.json
│
├── tools/                      # Development tools (user-facing)
│   ├── cli/                    # Command line tool
│   │   ├── commands/           # CLI commands
│   │   ├── lib/                # CLI libraries
│   │   ├── bin/                # Executable scripts
│   │   ├── tests/
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   └── frontend/               # Web dashboard (future)
│       ├── components/         # React components
│       ├── pages/              # Next.js pages
│       ├── lib/                # Frontend utilities
│       ├── public/             # Static assets
│       ├── tests/
│       ├── package.json
│       └── Dockerfile
│
├── examples/                   # Example projects for testing
│   ├── nodejs/                 # Node.js example
│   ├── python/                 # Python example
│   ├── go/                     # Go example
│   └── static/                 # Static site example
│
├── infrastructure/             # Infrastructure as Code
│   ├── docker/                # Docker configurations
│   ├── kubernetes/            # K8s manifests
│   ├── terraform/             # Infrastructure provisioning
│   └── scripts/               # Deployment scripts
│
├── docs/                      # Additional documentation
├── tests/                     # Integration tests
├── scripts/                   # Development scripts
└── README.md                  # This file
```

### Structure Benefits

- **Purpose-Based Organization** - Services vs tools are clearly separated
- **Consistent Patterns** - All services follow the same structure
- **Clear Dependencies** - Easy to understand what depends on what
- **Scalable Design** - Easy to add new services or tools
- **Developer Friendly** - Intuitive navigation and organization

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (optional, for local development)
- Node.js 18+ (optional, for CLI development)

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
# Install CLI globally (from npm)
npm install -g dprod-cli

# Or install locally for development
cd tools/cli
npm install
npm link

# Test CLI
dprod --help

# Login with email
dprod login -e test@example.com
```

### 5. Deploy Your First Project

```bash
# Create a simple Node.js project
mkdir test-app
cd test-app
echo '{"name":"test","version":"1.0.0","scripts":{"start":"node index.js"}}' > package.json
echo 'console.log("Hello from Dprod!");' > index.js

# Deploy it
dprod deploy

# Your app will be available at:
# Development: http://localhost:PORT
# Production: https://test.dprod.app
```

---

## 🛠️ Development

### Available Commands

```bash
# Development
make dev              # Start full development environment
make dev-api          # Start API server only
make dev-cli          # Start CLI development
make dev-frontend     # Start frontend development

# Testing
make test             # Run all tests
make test-api         # Run API tests
make test-cli         # Run CLI tests

# Code Quality
make lint             # Run linting
make clean            # Clean up development environment

# Building
make build            # Build all packages
make install          # Install all dependencies
```

### Manual Setup

1. **Install dependencies**
   ```bash
   # Python dependencies
   poetry install
   
   # Node.js dependencies
   cd tools/cli && npm install
   cd tools/frontend && npm install
   ```

2. **Start services**
   ```bash
   # Start database and Redis
   docker-compose up -d postgres redis
   
   # Start API server
   make dev-api
   
   # Start frontend (in another terminal)
   make dev-frontend
   ```

### Development Workflow

1. **Make changes** to the relevant service
2. **Test locally** using the development commands
3. **Run tests** to ensure nothing is broken
4. **Update documentation** if needed
5. **Commit changes** with clear messages

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Configuration
DEBUG=true
PORT=8000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql+asyncpg://dprod:dprod@localhost:5432/dprod

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Docker Configuration
DOCKER_SOCKET_PATH=/var/run/docker.sock

# File Upload
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_PATH=/tmp/dprod/uploads

# API URLs
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# CLI Configuration
DPROD_API_URL=http://localhost:8000

# URL Generation Configuration
# Free tier: All users get *.dprod.app subdomains
# Premium tier: Users can add custom domains

# Development mode (uses localhost with ports)
NODE_ENV=development

# Production mode (uses dprod.app subdomains)
# NODE_ENV=production
```

### URL Generation

Dprod uses a freemium model for URL generation:

#### **Free Tier (Default)**
- **URL**: `https://your-app.dprod.app`
- **Features**: Automatic subdomain generation
- **Cost**: Free
- **Use Case**: Perfect for getting started, testing, and small projects

#### **Premium Tier (Future)**
- **URL**: `https://your-custom-domain.com`
- **Features**: Custom domain support
- **Cost**: Paid upgrade
- **Use Case**: Professional branding, enterprise requirements

#### **Development Mode**
- **URL**: `http://localhost:PORT`
- **Use Case**: Local development with Docker port mapping

#### **Configuration Examples**

**Development:**
```bash
NODE_ENV=development
# Result: http://localhost:32786
```

**Production (Free Tier):**
```bash
NODE_ENV=production
# Result: https://my-app.dprod.app
```

**Production (Premium Tier):**
```bash
NODE_ENV=production
# Custom domain set via API: myapp.com
# Result: https://myapp.com
```

### Service-Specific Configuration

Each service has its own configuration:

- **API**: `services/api/core/utils/config.py`
- **Orchestrator**: `services/orchestrator/core/config.py`
- **Detector**: `services/detector/core/config.py`
- **CLI**: `tools/cli/src/lib/config.js`

---

## 📦 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication

All API endpoints require authentication via API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/api/v1/endpoint
```

### Endpoints

#### Health Check
```http
GET /health
```

#### Authentication
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
GET /auth/me
Authorization: Bearer YOUR_API_KEY
```

#### Projects
```http
POST /projects
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "name": "my-project",
  "type": "nodejs"
}
```

```http
GET /projects
Authorization: Bearer YOUR_API_KEY
```

```http
GET /projects/{project_id}
Authorization: Bearer YOUR_API_KEY
```

#### Deployments
```http
POST /projects/{project_id}/deployments
Authorization: Bearer YOUR_API_KEY
Content-Type: multipart/form-data

file: [project-tarball]
```

```http
GET /deployments/{deployment_id}
Authorization: Bearer YOUR_API_KEY
```

```http
GET /deployments/{deployment_id}/logs
Authorization: Bearer YOUR_API_KEY
```

### Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": { ... }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 💻 CLI Reference

### Installation

```bash
# Install globally from npm (recommended)
npm install -g dprod-cli

# Or install from source for development
cd tools/cli
npm install
npm link

# Verify installation
dprod --help
```

### Commands

#### `dprod deploy [options] [project-name]`

Deploy current directory to Dprod.

**Options:**
- `-n, --name <name>` - Project name
- `-e, --env <file>` - Environment file to include
- `-d, --detach` - Don't stream logs, return immediately
- `-f, --force` - Force deployment despite warnings
- `-v, --verbose` - Show detailed build information

**Examples:**
```bash
# Basic deployment
dprod deploy

# Custom project name
dprod deploy --name my-awesome-app

# With environment variables
dprod deploy --env .env.production

# Detached mode
dprod deploy --detach
```

#### `dprod login [options]`

Authenticate with Dprod.

**Options:**
- `-t, --token <token>` - Authenticate with API token
- `-e, --email <email>` - Login with email

**Examples:**
```bash
# Interactive login
dprod login

# Token login
dprod login --token YOUR_API_KEY

# Email login
dprod login --email user@example.com
```

#### `dprod logout`

Logout from Dprod.

#### `dprod status [project-name]`

Check project status and deployments.

**Examples:**
```bash
# List all projects
dprod status

# Check specific project
dprod status my-project
```

#### `dprod logs [options] [project-name]`

View deployment logs.

**Options:**
- `-d, --deployment <id>` - Specific deployment ID
- `-f, --follow` - Follow logs in real-time
- `-t, --tail <number>` - Show last N lines (default: 100)

**Examples:**
```bash
# View logs
dprod logs my-project

# Follow logs
dprod logs my-project --follow

# Show last 50 lines
dprod logs my-project --tail 50
```

#### `dprod list`

List all your projects.

### Global Options

- `--api-url <url>` - Custom API URL (default: http://localhost:8000)
- `--debug` - Enable debug mode
- `-v, --version` - Show version information

---

## 🐳 Docker & Deployment

### Development Environment

The development environment uses Docker Compose:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dprod
      POSTGRES_USER: dprod
      POSTGRES_PASSWORD: dprod
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./services/api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://dprod:dprod@postgres:5432/dprod
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
```

### Production Deployment

For production deployment:

1. **Set up infrastructure** (servers, database, Redis)
2. **Configure environment variables**
3. **Deploy services** using Docker or Kubernetes
4. **Set up reverse proxy** (Nginx, Traefik)
5. **Configure SSL certificates**

### Docker Commands

```bash
# Build all services
docker-compose build

# Start development environment
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Clean up
docker-compose down -v
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test suites
make test-api
make test-cli

# Run with coverage
pytest --cov=services
```

### Test Structure

```
tests/
├── e2e/                    # End-to-end tests
├── fixtures/               # Test data
├── unit/                   # Unit tests
└── integration/            # Integration tests
```

### Writing Tests

#### Python Tests (pytest)

```python
import pytest
from services.api.core.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

#### Node.js Tests (Jest)

```javascript
const { deployHandler } = require('../lib/deploy-handler');

describe('Deploy Handler', () => {
  test('should detect Node.js project', async () => {
    const result = await deployHandler({
      projectPath: './examples/nodejs',
      projectName: 'test'
    });
    
    expect(result.success).toBe(true);
  });
});
```

---

## 📈 Examples

### Supported Project Types

#### Node.js
```bash
cd examples/nodejs
dprod deploy
```

#### Python
```bash
cd examples/python
dprod deploy
```

#### Go
```bash
cd examples/go
dprod deploy
```

#### Static Site
```bash
cd examples/static
dprod deploy
```

### Example Projects

The `examples/` directory contains sample projects for each supported technology:

- **Node.js**: Express.js application with package.json
- **Python**: FastAPI application with requirements.txt
- **Go**: Simple HTTP server with go.mod
- **Static**: HTML/CSS/JS static website

### Custom Project Detection

You can extend the detection engine by adding new detectors:

```python
# services/detector/core/detectors/rust.py
class RustDetector(BaseDetector):
    def __init__(self):
        super().__init__(ProjectType.RUST)
    
    def can_handle(self, project_path: Path) -> bool:
        return (project_path / "Cargo.toml").exists()
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        return ProjectConfig(
            type=ProjectType.RUST,
            build_command="cargo build --release",
            start_command="cargo run",
            port=8080,
            environment={"RUST_LOG": "info"}
        )
```

---

## 🔍 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker is running
docker ps

# Restart services
make clean && make dev

# Check Docker logs
docker-compose logs api
```

#### Database Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres

# Check database connection
docker-compose exec postgres psql -U dprod -d dprod -c "SELECT 1;"
```

#### CLI Issues
```bash
# Check API connection
curl http://localhost:8000/health

# Reinstall CLI dependencies
cd tools/cli && npm install

# Check CLI configuration
cat ~/.dprod/config.json
```

#### API Issues
```bash
# Check API logs
docker-compose logs api

# Restart API service
docker-compose restart api

# Check API health
curl http://localhost:8000/health
```

### Debug Mode

Enable debug mode for more verbose output:

```bash
# CLI debug mode
dprod --debug deploy

# API debug mode
DEBUG=true make dev-api
```

### Logs

View logs for different components:

```bash
# API logs
docker-compose logs -f api

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

---

## 🤝 Contributing

### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/dprod.git
   cd dprod
   ```

3. **Set up development environment**
   ```bash
   ./scripts/setup-dev.sh
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

5. **Make your changes**
6. **Run tests**
   ```bash
   make test
   ```

7. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

8. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

9. **Open a Pull Request**

### Development Guidelines

- **Follow the existing code style**
- **Write tests for new features**
- **Update documentation**
- **Use meaningful commit messages**
- **Keep PRs focused and small**

### Code Style

#### Python
- Use `black` for formatting
- Use `isort` for import sorting
- Use `flake8` for linting
- Follow PEP 8 guidelines

#### JavaScript
- Use `prettier` for formatting
- Use `eslint` for linting
- Follow standard JavaScript conventions

### Testing Requirements

- **Unit tests** for all new functions
- **Integration tests** for API endpoints
- **End-to-end tests** for complete workflows
- **Documentation** for new features

---

## 📞 Support

- 📖 **Documentation**: This file
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/dprod/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/dprod/discussions)
- 📧 **Email**: teamdprod@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the Dprod Team**

*Last updated: 2025-10-17*
