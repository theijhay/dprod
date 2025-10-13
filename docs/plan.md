# Dprod Development Workflow & Documentation
## Backend-Focused Implementation Plan

---

# Version 0.1: Foundation & Core Infrastructure

## 🎯 Objective
Establish the basic backend architecture, authentication system, and project detection engine.

## 📋 Epic: Backend Foundation

### Task 0.1.1: Project Structure Setup
**Description**: Initialize monorepo structure with all backend packages
```
deployzero-backend/
├── packages/
│   ├── api/                 # FastAPI backend
│   ├── orchestrator/        # Deployment engine  
│   ├── detection-engine/    # Project detection
│   ├── cli/                 # Command line tool
│   └── shared/              # Shared types & utilities
├── docker-compose.yml
├── Makefile
└── README.md
```

**Implementation Details**:
- Use Poetry for Python package management
- Each package should have independent `pyproject.toml`
- Shared package contains common types, database models, and utilities
- Docker setup for local development with PostgreSQL and Redis

**Acceptance Criteria**:
- [ ] All packages can be installed independently
- [ ] Docker compose starts all services
- [ ] Basic imports work between packages
- [ ] Development environment is reproducible

### Task 0.1.2: Database & Models
**Description**: Set up PostgreSQL with core data models

**Schema**:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(64) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(63) UNIQUE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deployments table  
CREATE TABLE deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'created', -- created, building, deploying, live, error
    commit_hash VARCHAR(40),
    logs TEXT,
    url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Implementation Details**:
- Use SQLAlchemy with async support
- Alembic for database migrations
- Pydantic models for API validation
- Repository pattern for data access

### Task 0.1.3: Authentication System
**Description**: Implement API key-based authentication

**Endpoints**:
- `POST /auth/register` - Create new user
- `POST /auth/login` - Login and get API key
- `POST /auth/refresh` - Refresh API key
- `Middleware` - API key validation on all routes

**Implementation**:
```python
# packages/api/src/auth/middleware.py
class APIKeyAuth:
    async def __call__(self, request: Request) -> User:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(status_code=401)
        
        user = await UserRepository.get_by_api_key(api_key)
        if not user:
            raise HTTPException(status_code=401)
            
        return user
```

---

## 📋 Epic: Project Detection Engine

### Task 0.1.4: Basic Detection System
**Description**: Create intelligent project type detection

**Supported Stacks**:
- Node.js (package.json detection)
- Python (requirements.txt, pyproject.toml, setup.py)
- Static sites (index.html)
- Go (go.mod)

**Implementation**:
```python
# packages/detection-engine/src/detector.py
class ProjectDetector:
    def detect(self, project_path: Path) -> ProjectConfig:
        detectors = [
            NodeJSDetector(),
            PythonDetector(),
            StaticDetector(), 
            GoDetector()
        ]
        
        for detector in detectors:
            if detector.can_handle(project_path):
                return detector.get_config(project_path)
        
        raise ProjectDetectionError("Could not detect project type")

class NodeJSDetector:
    def can_handle(self, path: Path) -> bool:
        return (path / "package.json").exists()
    
    def get_config(self, path: Path) -> ProjectConfig:
        with open(path / "package.json") as f:
            package = json.load(f)
        
        return ProjectConfig(
            type="nodejs",
            build_command="npm install",
            start_command=self._get_start_command(package),
            port=3000,
            environment={}
        )
```

### Task 0.1.5: Configuration Generation
**Description**: Generate deployment configuration from detected project

**Output Structure**:
```python
@dataclass
class ProjectConfig:
    type: str                    # nodejs, python, static, go
    build_command: Optional[str] # "npm install", "pip install -r requirements.txt"
    start_command: str           # "npm start", "python app.py"
    port: int                    # 3000, 8000, 8080
    environment: Dict[str, str]  # Environment variables
    install_path: str = "/app"   # Container installation path
```

---

## 🚀 Version 0.1 Deliverables
- [ ] Monorepo structure working
- [ ] Database with migrations
- [ ] User authentication system
- [ ] Project detection for 4 major stacks
- [ ] Basic API endpoints for users/projects
- [ ] Docker development environment

---

# Version 0.2: Deployment Orchestration

## 🎯 Objective
Build the core deployment engine that can build and run projects in isolated environments.

## 📋 Epic: Container Management

### Task 0.2.1: Docker Orchestrator
**Description**: Create service to manage Docker containers for deployments

**Implementation**:
```python
# packages/orchestrator/src/docker_manager.py
class DockerManager:
    async def create_deployment_container(
        self, 
        project: Project,
        config: ProjectConfig,
        source_code_path: Path
    ) -> DeploymentContainer:
        # 1. Build Dockerfile from project config
        dockerfile = self._generate_dockerfile(config)
        
        # 2. Build image
        image_id = await self._build_image(
            dockerfile, 
            source_code_path,
            f"deployzero-{project.id}:latest"
        )
        
        # 3. Run container
        container_id = await self._run_container(
            image_id,
            ports={f"{config.port}/tcp": None},  # Dynamic port mapping
            environment=config.environment
        )
        
        # 4. Get assigned port
        port = await self._get_container_port(container_id)
        
        return DeploymentContainer(container_id, port)

    def _generate_dockerfile(self, config: ProjectConfig) -> str:
        templates = {
            "nodejs": NODEJS_DOCKERFILE,
            "python": PYTHON_DOCKERFILE, 
            "static": STATIC_DOCKERFILE,
            "go": GO_DOCKERFILE
        }
        return templates[config.type].format(config=config)
```

### Task 0.2.2: Dynamic Dockerfile Templates
**Description**: Create optimized Dockerfiles for each project type

**Node.js Template**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN {build_command}
EXPOSE {port}
CMD {start_command}
```

**Python Template**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN {build_command}
EXPOSE {port}  
CMD {start_command}
```

### Task 0.2.3: Resource Management
**Description**: Implement container resource limits and cleanup

**Features**:
- Memory limits (512MB per container)
- CPU limits (0.5 CPU per container)
- Auto-cleanup of old containers
- Health check monitoring

---

## 📋 Epic: Deployment Pipeline

### Task 0.2.4: Deployment State Machine
**Description**: Manage deployment lifecycle with state transitions

**States**: `created → building → deploying → live | error`

**Implementation**:
```python
# packages/orchestrator/src/deployment_manager.py
class DeploymentManager:
    async def deploy_project(
        self, 
        project: Project, 
        source_code: bytes
    ) -> Deployment:
        deployment = await self._create_deployment_record(project)
        
        try:
            # 1. Save and extract source code
            code_path = await self._save_source_code(source_code)
            
            # 2. Detect project configuration
            config = await self._detect_project_config(code_path)
            await self._update_deployment_status(deployment, "building", config)
            
            # 3. Build and run container
            container = await self.docker_manager.create_deployment_container(
                project, config, code_path
            )
            
            # 4. Update deployment with URL
            url = f"https://{project.subdomain}.deployzero.app"
            await self._update_deployment_status(
                deployment, "live", url=url, container_id=container.id
            )
            
            return deployment
            
        except Exception as e:
            await self._update_deployment_status(deployment, "error", str(e))
            raise
```

### Task 0.2.5: Log Management
**Description**: Capture and store build/deployment logs

**Implementation**:
```python
# packages/orchestrator/src/log_manager.py
class LogManager:
    async def capture_container_logs(self, container_id: str, deployment_id: UUID):
        async with async_docker.containers.get(container_id) as container:
            async for line in container.log(stdout=True, stderr=True, follow=True):
                await self._store_log(deployment_id, line)
    
    async def stream_logs_to_client(self, deployment_id: UUID, websocket):
        async for log_entry in self._get_logs(deployment_id):
            await websocket.send_text(json.dumps({
                "type": "log",
                "data": log_entry
            }))
```

---

## 📋 Epic: Reverse Proxy & Routing

### Task 0.2.6: Dynamic Routing with Traefik
**Description**: Set up Traefik to route subdomains to deployment containers

**docker-compose.yml**:
```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro

  orchestrator:
    build: ./packages/orchestrator
    environment:
      - TRAEFIK_ENABLED=true
    labels:
      - "traefik.enable=true"
```

**Dynamic Routing**:
```python
# Add labels to containers for Traefik discovery
labels = {
    "traefik.enable": "true",
    f"traefik.http.routers.{project.subdomain}.rule": f"Host(`{project.subdomain}.deployzero.app`)",
    f"traefik.http.routers.{project.subdomain}.entrypoints": "websecure",
    f"traefik.http.services.{project.subdomain}.loadbalancer.server.port": str(container_port)
}
```

---

## 🚀 Version 0.2 Deliverables
- [ ] Docker container management system
- [ ] Dynamic Dockerfile generation
- [ ] Deployment state machine
- [ ] Real-time log streaming
- [ ] Traefik reverse proxy setup
- [ ] Subdomain-based routing
- [ ] Resource limits and cleanup

---

# Version 0.3: CLI Tool & API Integration

## 🎯 Objective
Build the CLI tool and integrate all components into a seamless deployment workflow.

## 📋 Epic: CLI Development

### Task 0.3.1: CLI Foundation
**Description**: Create the `deployzero` command line interface

**Implementation** (Node.js for wider compatibility):
```javascript
// packages/cli/src/index.js
#!/usr/bin/env node

const { Command } = require('commander');
const { deploy } = require('./commands/deploy');
const { login } = require('./commands/login');
const { status } = require('./commands/status');

const program = new Command();

program
  .name('deployzero')
  .description('Zero-config deployment platform')
  .version('0.3.0');

program
  .command('deploy')
  .description('Deploy current directory')
  .option('--name <name>', 'Project name')
  .action(deploy);

program
  .command('login')
  .description('Authenticate with DeployZero')
  .action(login);

program
  .command('status [project]')
  .description('Check deployment status')
  .action(status);

program.parse();
```

### Task 0.3.2: Deployment Command
**Description**: Implement the core `deploy` command

**Implementation**:
```javascript
// packages/cli/src/commands/deploy.js
async function deploy(options) {
  try {
    // 1. Check authentication
    const apiKey = await ensureAuthenticated();
    
    // 2. Package current directory
    const tarStream = await packageCurrentDirectory();
    
    // 3. Create project or get existing
    const project = await findOrCreateProject(options.name, apiKey);
    
    // 4. Upload and trigger deployment
    const deployment = await triggerDeployment(project, tarStream, apiKey);
    
    // 5. Stream logs in real-time
    await streamDeploymentLogs(deployment.id, apiKey);
    
    // 6. Show success message
    console.log(`✅ Deployed! ${deployment.url}`);
    
  } catch (error) {
    console.error('❌ Deployment failed:', error.message);
    process.exit(1);
  }
}
```

### Task 0.3.3: Authentication Flow
**Description**: Implement login and API key management

**Implementation**:
```javascript
// packages/cli/src/auth.js
class AuthManager {
  async login() {
    // 1. Open browser for OAuth-like flow
    openBrowser('https://api.deployzero.app/auth/cli-login');
    
    // 2. Poll for authentication completion
    const apiKey = await this.pollForAuthCode();
    
    // 3. Save API key to config file
    await this.saveConfig({ apiKey });
    
    console.log('✅ Logged in successfully!');
  }
  
  async getApiKey() {
    const config = await this.loadConfig();
    if (!config.apiKey) {
      throw new Error('Not authenticated. Run "deployzero login" first.');
    }
    return config.apiKey;
  }
}
```

---

## 📋 Epic: API Integration

### Task 0.3.4: Deployment API Endpoints
**Description**: Create REST API for deployment operations

**Endpoints**:
- `POST /projects` - Create new project
- `POST /projects/{id}/deployments` - Trigger new deployment
- `GET /deployments/{id}` - Get deployment status
- `GET /deployments/{id}/logs` - Stream deployment logs
- `WS /deployments/{id}/logs/stream` - WebSocket for real-time logs

**Implementation**:
```python
# packages/api/src/routes/deployments.py
@router.post("/projects/{project_id}/deployments")
async def create_deployment(
    project_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(auth.get_current_user)
):
    # Verify project ownership
    project = await ProjectRepository.get_by_id(project_id)
    if project.user_id != user.id:
        raise HTTPException(404)
    
    # Read uploaded file
    source_code = await file.read()
    
    # Trigger deployment
    deployment = await DeploymentOrchestrator.deploy(project, source_code)
    
    return {
        "deployment_id": deployment.id,
        "status": deployment.status,
        "url": deployment.url
    }

@router.websocket("/deployments/{deployment_id}/logs")
async def stream_deployment_logs(
    websocket: WebSocket,
    deployment_id: UUID
):
    await websocket.accept()
    
    # Verify user has access to deployment
    deployment = await verify_deployment_access(deployment_id, websocket)
    
    # Stream logs in real-time
    async for log_line in LogManager.get_log_stream(deployment_id):
        await websocket.send_text(log_line)
```

### Task 0.3.5: File Upload Handling
**Description**: Handle large file uploads efficiently

**Implementation**:
```python
# packages/api/src/services/file_upload.py
class FileUploadService:
    async def save_uploaded_file(self, file: UploadFile) -> Path:
        # Create temp directory
        temp_dir = Path(f"/tmp/deployzero/{uuid4()}")
        temp_dir.mkdir(parents=True)
        
        # Save uploaded tar file
        tar_path = temp_dir / "source.tar.gz"
        with open(tar_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract
        extract_path = temp_dir / "source"
        await self._extract_tar(tar_path, extract_path)
        
        return extract_path
```

---

## 📋 Epic: Error Handling & Validation

### Task 0.3.6: Comprehensive Error Handling
**Description**: Implement graceful error handling across all components

**Error Types**:
- Project detection errors
- Build failures
- Container runtime errors
- Network issues
- Resource exhaustion

**Implementation**:
```python
# packages/shared/src/exceptions.py
class DeployZeroException(Exception):
    """Base exception for all DeployZero errors"""
    
class ProjectDetectionError(DeployZeroException):
    """Failed to detect project type"""
    
class BuildError(DeployZeroException):
    """Build process failed"""
    
class ContainerError(DeployZeroException):
    """Container runtime error"""
    
class ResourceLimitError(DeployZeroException):
    """Resource limits exceeded"""
```

### Task 0.3.7: Input Validation
**Description**: Validate all inputs with Pydantic models

**Implementation**:
```python
# packages/shared/src/models.py
class DeploymentCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=50)
    source_code: bytes
    
    @validator('project_name')
    def validate_project_name(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Project name can only contain lowercase letters, numbers, and hyphens')
        return v
```

---

## 🚀 Version 0.3 Deliverables
- [ ] Fully functional CLI tool
- [ ] Authentication system
- [ ] File upload and processing
- [ ] Deployment API endpoints
- [ ] Real-time log streaming via WebSocket
- [ ] Comprehensive error handling
- [ ] Input validation and security

---

## 📊 Progress Tracking

### Development Board Columns
```
Backlog → In Progress → Code Review → Testing → Done
```

### Definition of Done for Each Task
- [ ] Code implemented and reviewed
- [ ] Unit tests written and passing
- [ ] Integration tests for API endpoints
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] No known critical issues

### Testing Strategy
- **Unit Tests**: Each package independently tested
- **Integration Tests**: API endpoints with test database
- **End-to-End Tests**: Full deployment flow with sample projects
- **Manual Testing**: Deploy real projects from each supported stack

---
