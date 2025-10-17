# Dprod - Zero-Config Deployment Platform

> Deploy any project with a single command, regardless of technology stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

## 🎯 What is Dprod?

Dprod is a zero-configuration deployment platform that allows developers to deploy ANY project with a single command, regardless of the technology stack, without any configuration files or setup.

### The Problem
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

**No configuration files. No server setup. No infrastructure knowledge required.**

## 🏗️ Architecture

Dprod is a comprehensive deployment platform with the following components:

### Core Services
- **API Server** (FastAPI) - Central hub for authentication, project management, and deployment orchestration
- **Detection Engine** (Python) - Automatically detects project types and generates configurations
- **Orchestrator Service** (Python) - Manages Docker containers and deployment lifecycle
- **Reverse Proxy** (Traefik) - Routes traffic to deployed applications with SSL
- **Database** (PostgreSQL) - Stores user data, projects, and deployment history
- **Cache** (Redis) - High-performance caching and session management
- **File Storage** - Stores project source code and build artifacts

### User Interfaces
- **CLI Tool** (Node.js) - Command-line interface for developers
- **Web Dashboard** (React) - Web-based management interface
- **API Gateway** (Future) - External API access for integrations

### Deployment Layer
- **User Applications** - Docker containers running user projects with automatic subdomain routing

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/dprod.git
   cd dprod
   ```

2. **Run the setup script**
   ```bash
   ./scripts/setup-dev.sh
   ```

3. **Start the development environment**
   ```bash
   make dev
   ```

4. **Access the services**
   - API Server: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend Dashboard: http://localhost:3000

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

## 📦 Project Structure

```
dprod/
├── services/                   # Backend services
│   ├── api/                    # FastAPI backend service
│   ├── orchestrator/           # Deployment orchestration service
│   ├── detector/               # Project detection service
│   └── shared/                 # Shared types & utilities
├── tools/                      # Development tools
│   ├── cli/                    # Node.js CLI tool
│   └── frontend/               # Next.js web dashboard
├── infrastructure/             # Infrastructure as Code
├── examples/                   # Example projects for testing
├── docs/                       # Documentation
├── tests/                      # Integration tests
└── scripts/                    # Development scripts
```

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

### API Endpoints

- `GET /health` - Health check
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /projects` - Create new project
- `GET /projects` - List user projects
- `POST /projects/{id}/deployments` - Create deployment
- `GET /deployments/{id}/logs` - Get deployment logs

## 🎯 Supported Project Types

- **Node.js** - Detects `package.json`, runs `npm install` and `npm start`
- **Python** - Detects `requirements.txt`, runs `pip install` and `python app.py`
- **Go** - Detects `go.mod`, runs `go mod download` and `go run main.go`
- **Static Sites** - Detects `index.html`, serves static files

## 🔧 Configuration

Environment variables can be set in `.env` file:

```env
DEBUG=true
DATABASE_URL=postgresql+asyncpg://dprod:dprod@localhost:5432/dprod
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 Documentation

- [Complete Documentation](DOCS.md) - Comprehensive guide covering architecture, development, API reference, and more

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Complete Documentation](DOCS.md)
- 🐛 [Issue Tracker](https://github.com/your-org/dprod/issues)
- 💬 [Discussions](https://github.com/your-org/dprod/discussions)

---

**Made with ❤️ by the Dprod Team**