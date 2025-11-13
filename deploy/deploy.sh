#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}➜${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }


AWS_REGION="us-east-1"
CLUSTER_NAME="dprod"
SERVICE_NAME="dprod-api"
TASK_FAMILY="dprod-task"
ENVIRONMENT="production"  # Used for parameter path: /dprod/production/*

# ECR and Image
ECR_REPO_NAME="dprod-api"

# Container Settings
CPU="256"          # 256, 512, 1024, 2048, 4096
MEMORY="512"       # 512, 1024, 2048, 4096, 8192
DESIRED_COUNT="1"

echo ""
log "🚀 Starting dprod deployment..."
echo ""

# Get AWS Account ID
log "Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
success "AWS Account: $AWS_ACCOUNT_ID"

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Check if cluster exists
log "Checking cluster..."
if aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION | grep -q "ACTIVE"; then
    success "Cluster found: $CLUSTER_NAME"
else
    error "Cluster $CLUSTER_NAME not found"
fi

# Login to ECR
log "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Pull latest image for cache
log "Pulling latest image for cache..."
docker pull $ECR_URI:latest 2>/dev/null || warn "No previous image found (first build?)"

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Clean Python cache files to ensure consistent builds
log "Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Build Docker image with cache
log "Building Docker image..."
DOCKER_BUILDKIT=1 docker build \
  --cache-from $ECR_URI:latest \
  -t $ECR_REPO_NAME:latest .

# Tag for ECR
log "Tagging image..."
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
docker tag $ECR_REPO_NAME:latest $ECR_URI:latest
docker tag $ECR_REPO_NAME:latest $ECR_URI:$TIMESTAMP

# Push to ECR
log "Pushing to ECR..."
docker push $ECR_URI:latest
docker push $ECR_URI:$TIMESTAMP
success "Image pushed: $ECR_URI:latest"

# Create task definition
log "Creating task definition..."
TASK_DEF=$(cat <<EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "$CPU",
  "memory": "$MEMORY",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "dprod-api",
      "image": "$ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "NODE_ENV", "value": "production"},
        {"name": "ALLOW_ALL_HOSTS", "value": "true"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f -H 'Host: localhost' http://localhost:8000/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/DATABASE_URL"},
        {"name": "REDIS_URL", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/REDIS_URL"},
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/SECRET_KEY"},
        {"name": "AI_ENABLED", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/AI_ENABLED"},
        {"name": "DEBUG", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/DEBUG"},
        {"name": "LLM_PROVIDER", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/LLM_PROVIDER"},
        {"name": "LLM_MODEL", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/LLM_MODEL"},
        {"name": "LLM_API_KEY", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/LLM_API_KEY"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/$TASK_FAMILY",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      },
      "essential": true
    }
  ]
}
EOF
)

# Save to temp file and register
echo "$TASK_DEF" > /tmp/dprod-task-def.json
aws ecs register-task-definition --region $AWS_REGION --cli-input-json file:///tmp/dprod-task-def.json > /dev/null
success "Task definition registered"

# Run database migrations
log "Running database migrations..."
MIGRATION_TASK_DEF=$(cat <<EOF
{
  "family": "dprod-migration",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "migration",
      "image": "$ECR_URI:latest",
      "command": ["sh", "-c", "alembic upgrade head"],
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:ssm:$AWS_REGION:$AWS_ACCOUNT_ID:parameter/dprod/$ENVIRONMENT/DATABASE_URL"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dprod-migration",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "migration",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
EOF
)

# Register migration task definition
echo "$MIGRATION_TASK_DEF" > /tmp/dprod-migration-task-def.json
aws ecs register-task-definition --region $AWS_REGION --cli-input-json file:///tmp/dprod-migration-task-def.json > /dev/null

# Get VPC configuration from existing service
VPC_CONFIG=$(aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION \
  --query 'services[0].networkConfiguration.awsvpcConfiguration' \
  --output json)

SUBNETS=$(echo $VPC_CONFIG | jq -r '.subnets | join(",")')
SECURITY_GROUPS=$(echo $VPC_CONFIG | jq -r '.securityGroups | join(",")')

# Run migration task
log "Executing migration task..."
MIGRATION_TASK_ARN=$(aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition dprod-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUPS],assignPublicIp=ENABLED}" \
  --region $AWS_REGION \
  --query 'tasks[0].taskArn' \
  --output text)

if [ -n "$MIGRATION_TASK_ARN" ]; then
  log "Waiting for migration to complete..."
  aws ecs wait tasks-stopped \
    --cluster $CLUSTER_NAME \
    --tasks $MIGRATION_TASK_ARN \
    --region $AWS_REGION
  
  # Check migration task exit code
  EXIT_CODE=$(aws ecs describe-tasks \
    --cluster $CLUSTER_NAME \
    --tasks $MIGRATION_TASK_ARN \
    --region $AWS_REGION \
    --query 'tasks[0].containers[0].exitCode' \
    --output text)
  
  if [ "$EXIT_CODE" = "0" ]; then
    success "Database migrations completed successfully"
  else
    error "Migration failed with exit code: $EXIT_CODE. Check logs at /ecs/dprod-migration"
  fi
else
  warn "Could not start migration task"
fi

# Check if service exists
log "Checking if service exists..."
if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION 2>/dev/null | grep -q "ACTIVE"; then
    # Update existing service
    log "Updating existing service..."
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $TASK_FAMILY \
        --desired-count $DESIRED_COUNT \
        --region $AWS_REGION > /dev/null
    success "Service updated"
else
    warn "Service doesn't exist. You need to create it first."
    echo ""
    echo "Run this command to create the service:"
    echo ""
    echo "aws ecs create-service \\"
    echo "  --cluster $CLUSTER_NAME \\"
    echo "  --service-name $SERVICE_NAME \\"
    echo "  --task-definition $TASK_FAMILY \\"
    echo "  --desired-count $DESIRED_COUNT \\"
    echo "  --launch-type FARGATE \\"
    echo "  --network-configuration \"awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}\" \\"
    echo "  --region $AWS_REGION"
    echo ""
    echo "Replace subnet-xxx, subnet-yyy, and sg-xxx with your actual values."
    exit 0
fi

echo ""
success "🎉 Deployment complete!"
echo ""
log "View logs:"
echo "  aws logs tail /ecs/$TASK_FAMILY --follow --region $AWS_REGION"
echo ""
log "Check status:"
echo "  aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION"
echo ""
