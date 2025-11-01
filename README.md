# Dprod - Zero-Configuration Deployment Platform

> Deploy any project with a single command, regardless of technology stack.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

## 🎯 **What is Dprod?**

Dprod is a zero-configuration deployment platform that automatically detects your project type and deploys it to the cloud with a single command. No Dockerfiles, no configuration files, no server setup required.

### **The Problem We Solve**

- Developers waste hours configuring deployment environments
- Writing Dockerfiles, setting up CI/CD, managing infrastructure
- Most deployment solutions require significant configuration and platform-specific knowledge
- What takes 5 minutes to run locally takes 5+ hours to deploy properly

### **The Solution**

```bash
cd /your/project
dprod deploy
# → 🔍 Analyzing your project...
# → 📦 Packaging your code...
# → 🚀 Deploying to Cloud...
# → ✅ Success! Your app is live at: https://your-project-abc123.dprod.app
```

**No configuration files. No server setup. No infrastructure knowledge required.**

## ✨ **Key Features**

- ✅ **Universal Project Detection** - Automatically detects Node.js, Python, Go, and Static sites
- ✅ **Zero Configuration** - No Dockerfiles, config files, or setup required
- ✅ **Real-time Logs** - Stream deployment progress in real-time
- ✅ **Auto SSL** - Automatic HTTPS with custom subdomains
- ✅ **Resource Management** - Automatic container limits and cleanup
- ✅ **CLI Tool** - Beautiful command-line interface with live progress updates
- ✅ **Project Management** - Track multiple projects and deployments
- ✅ **API Authentication** - Secure email-based login with API keys

## 🚀 **Quick Start**

### **Install CLI**

```bash
npm install -g dprod-cli
```

### **Deploy Your First Project**

```bash
# Navigate to your project
cd my-awesome-app

# Login (first time only)
dprod login -e your@email.com

# Deploy with zero config
dprod deploy

# Your app is now live! 🎉
```

## 💡 **Real-World Usage**

### **Deploy a Node.js API**

```bash
cd my-node-api
dprod deploy
# ✅ Deployed to: https://my-node-api.dprod.app
```

### **Deploy a Python Web App**

```bash
cd my-flask-app
dprod deploy
# ✅ Deployed to: https://my-flask-app.dprod.app
```

### **Deploy a Static Website**

```bash
cd my-html-site
dprod deploy
# ✅ Deployed to: https://my-html-site.dprod.app
```

### **Check Deployment Status**

```bash
# List all your projects
dprod list

# Check deployment status
dprod status my-project

# View deployment logs
dprod logs my-project
```

## 🎯 **Supported Project Types**

| Type | Detection | Build Command | Start Command |
|------|-----------|---------------|---------------|
| **Node.js** | `package.json` | `npm install` | `npm start` |
| **Python** | `requirements.txt` | `pip install -r requirements.txt` | `python app.py` |
| **Go** | `go.mod` | `go build` | Executes binary |
| **Static** | HTML files | N/A | Serves with Nginx |

The detection engine automatically identifies your project type and configures the appropriate build and runtime settings.

## 🏗️ **Tech Stack**

### **Backend Services**
- **API Service** - FastAPI-based REST API with JWT authentication
- **Orchestrator** - Docker container orchestration and deployment management
- **Detector** - Intelligent project type detection and configuration generation
- **Shared** - Common types, models, and utilities across services

### **Technologies**

**Backend:**
- Python 3.11+
- FastAPI - Modern, fast web framework
- SQLAlchemy - Database ORM with async support
- PostgreSQL - Relational database
- Redis - Caching and session management

**CLI:**
- Node.js 18+
- Commander.js - CLI framework
- Axios - HTTP client

**Containerization:**
- Docker - Container runtime
- Docker Compose - Local development

## 📦 **Project Structure**

```
dprod/
├── services/                   # Backend microservices
│   ├── api/                    # FastAPI REST API
│   ├── orchestrator/           # Deployment orchestration
│   ├── detector/               # Project detection engine
│   └── shared/                 # Shared utilities
├── tools/                      # User-facing tools
│   ├── cli/                    # Node.js CLI (published to npm)
│   └── frontend/               # Web dashboard (future)
└── examples/                   # Example projects
```

## 🛠️ **Development**

### **Local Development Setup**

```bash
# Set up development environment
make setup

# Start development environment
make dev

# Start specific services
make dev-api          # API server only
make dev-cli          # CLI development

# Run tests
make test             # All tests
make test-api         # API tests only
```

### **Project Setup**

1. **Copy environment file**
   ```bash
   cp env.example .env
   # Edit .env if needed (works out of the box with Docker Compose defaults)
   ```

2. **Install dependencies**
   ```bash
   # Python dependencies
   poetry install
   
   # Node.js dependencies
   cd tools/cli && npm install
   ```

3. **Start services**
   ```bash
   # Start database and Redis
   docker-compose up -d postgres redis
   
   # Start API server
   make dev-api
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

## 📚 **Documentation**

- [Full Documentation](DOCS.md) - Comprehensive guide to Dprod
- [API Reference](DOCS.md#-api-reference) - REST API documentation
- [CLI Reference](DOCS.md#-cli-reference) - Command-line interface guide

## 🤝 **Contributing**

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ to make deployment simple**
