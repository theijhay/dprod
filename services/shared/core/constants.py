"""Constants for Dprod."""

# API Configuration
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Database Configuration
DATABASE_URL = "postgresql+asyncpg://dprod:dprod@localhost:5432/dprod"

# Redis Configuration
REDIS_URL = "redis://localhost:6379"

# Docker Configuration
DOCKER_SOCKET_PATH = "/var/run/docker.sock"
DEFAULT_CONTAINER_MEMORY_LIMIT = "512m"
DEFAULT_CONTAINER_CPU_LIMIT = "0.5"

# Project Detection
SUPPORTED_PROJECT_TYPES = [
    "nodejs",
    "python", 
    "go",
    "static"
]

# File Extensions for Detection
PROJECT_INDICATORS = {
    "nodejs": ["package.json"],
    "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
    "go": ["go.mod", "go.sum"],
    "static": ["index.html", "index.htm"]
}

# Default Ports
DEFAULT_PORTS = {
    "nodejs": 3000,
    "python": 8000,
    "go": 8080,
    "static": 80
}

# Build Commands
DEFAULT_BUILD_COMMANDS = {
    "nodejs": "npm install",
    "python": "pip install -r requirements.txt",
    "go": "go mod download",
    "static": None
}

# Start Commands
DEFAULT_START_COMMANDS = {
    "nodejs": "npm start",
    "python": "python app.py",
    "go": "go run main.go",
    "static": "npx serve -s . -l 80"
}

# Environment Variables
ENVIRONMENT_VARIABLES = {
    "NODE_ENV": "production",
    "PYTHONUNBUFFERED": "1",
    "PORT": "3000"
}
