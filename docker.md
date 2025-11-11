# Docker Compose Usage

### Basic (Development - localhost:PORT)

```bash
# Start postgres, redis, api
docker-compose up -d

# Your apps get random ports: http://localhost:32768
dprod deploy
```

### With Traefik (Subdomains - demo.dprod.local)

```bash
# Start postgres, redis, api + traefik
docker-compose --profile traefik up -d

# Add to /etc/hosts
echo "127.0.0.1 demo-nest.dprod.local" | sudo tee -a /etc/hosts

# Deploy with Traefik routing
USE_TRAEFIK=true dprod deploy

# Access at: http://demo-nest.dprod.local
```

---

## Docker Compose Profiles Explained

**Profiles** let you have optional services in ONE file:

```yaml
services:
  postgres:
    # Always starts
  
  traefik:
    profiles:
      - traefik  # Only starts when: --profile traefik
```

### Commands

```bash
# Start without Traefik (default)
docker-compose up -d
# Starts: postgres, redis, api

# Start WITH Traefik
docker-compose --profile traefik up -d
# Starts: postgres, redis, api, traefik

# Stop everything
docker-compose down

# View logs
docker-compose logs -f api
```

---

## Environment Variables

Create `.env` file:

```bash
# Basic
NODE_ENV=development
DEBUG=true

# Enable Traefik routing
USE_TRAEFIK=true

# AI Features (optional)
AI_ENABLED=false
OPENAI_API_KEY=your-key-here

# Database
DATABASE_URL=postgresql+asyncpg://dprodapi:dprodapi123@postgres:5432/dprod_db
REDIS_URL=redis://redis:6379
```

Then:
```bash
docker-compose up -d  # Reads .env automatically
```

---

## Production

For production, set:

```bash
# .env.production
NODE_ENV=production
USE_TRAEFIK=true
DEBUG=false
SECRET_KEY=generate-secure-key-here

# SSL
ACME_EMAIL=admin@dprod.app
DOMAIN=dprod.app
```

Then:
```bash
docker-compose --env-file .env.production --profile traefik up -d
```


---

## Common Tasks

```bash
# Restart API only
docker-compose restart api

# Rebuild API after code changes
docker-compose up -d --build api

# View all containers
docker-compose ps

# Remove everything (including volumes)
docker-compose down -v

# Check Traefik dashboard
# http://localhost:8080 (when Traefik is running)
```

### For Production:
1. Push to container registry (ECR/DockerHub):
   ```bash
   docker tag dprod_api:latest your-registry/dprod-api:v1.0.0
   docker push your-registry/dprod-api:v1.0.0
   ```

2. Use BuildKit for even faster builds:
   ```bash
   DOCKER_BUILDKIT=1 docker build -t dprod-api .
   # Parallel layer builds, better caching
   ```

3. Add .dockerignore to other services (detector, orchestrator)