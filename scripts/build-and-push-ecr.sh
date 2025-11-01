#!/bin/bash

# Build and Push Docker Images to ECR for Staging
# ===============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="us-east-1"
ECR_REGISTRY=""
REPOSITORIES=("dprod-api" "dprod-orchestrator" "dprod-detection")

echo -e "${BLUE}🐳 Building and Pushing Docker Images to ECR${NC}"
echo "=================================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Get AWS account ID
echo -e "${YELLOW}📋 Getting AWS Account ID...${NC}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo -e "${GREEN}✅ AWS Account ID: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${GREEN}✅ ECR Registry: ${ECR_REGISTRY}${NC}"

# Login to ECR
echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build and push each image
for repo in "${REPOSITORIES[@]}"; do
    echo -e "${BLUE}📦 Building ${repo}...${NC}"
    
    # Determine Dockerfile path based on repository
    case $repo in
        "dprod-api")
            DOCKERFILE="infrastructure/docker/Dockerfile.api"
            CONTEXT="."
            ;;
        "dprod-orchestrator")
            DOCKERFILE="infrastructure/docker/Dockerfile.orchestrator"
            CONTEXT="."
            ;;
        "dprod-detection")
            DOCKERFILE="infrastructure/docker/Dockerfile.detection"
            CONTEXT="."
            ;;
        *)
            echo -e "${RED}❌ Unknown repository: ${repo}${NC}"
            continue
            ;;
    esac
    
    # Build the image
    echo -e "${YELLOW}🔨 Building Docker image for ${repo}...${NC}"
    docker build -f ${DOCKERFILE} -t ${repo}:latest ${CONTEXT}
    
    # Create timestamp once
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    
    # Tag for ECR
    docker tag ${repo}:latest ${ECR_REGISTRY}/${repo}:latest
    docker tag ${repo}:latest ${ECR_REGISTRY}/${repo}:${TIMESTAMP}
    
    # Push to ECR
    echo -e "${YELLOW}📤 Pushing ${repo} to ECR...${NC}"
    docker push ${ECR_REGISTRY}/${repo}:latest
    docker push ${ECR_REGISTRY}/${repo}:${TIMESTAMP}
    
    echo -e "${GREEN}✅ Successfully pushed ${repo}${NC}"
done

echo -e "${GREEN}🎉 All images built and pushed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Run: terraform apply to create ECS infrastructure"
echo "2. Check ECS console for running services"
echo "3. Access your staging environment via ALB DNS name"
echo ""
echo -e "${YELLOW}💡 To get ALB DNS name:${NC}"
echo "aws elbv2 describe-load-balancers --names dprod-staging-alb --query 'LoadBalancers[0].DNSName' --output text"
