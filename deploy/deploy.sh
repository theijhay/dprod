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

# Build Docker image
log "Building Docker image..."
cd ..
docker build -t $ECR_REPO_NAME:latest .

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
        {"name": "NODE_ENV", "value": "production"}
      ],
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
