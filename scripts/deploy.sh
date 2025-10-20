#!/bin/bash

# Dprod AWS Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ENVIRONMENT=${ENVIRONMENT:-production}
DOMAIN_NAME=${DOMAIN_NAME:-dprod.app}

echo -e "${BLUE}🚀 Starting Dprod AWS Deployment${NC}"
echo "Region: $AWS_REGION"
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN_NAME"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check if required tools are installed
    command -v terraform >/dev/null 2>&1 || { echo -e "${RED}❌ Terraform is required but not installed.${NC}"; exit 1; }
    command -v aws >/dev/null 2>&1 || { echo -e "${RED}❌ AWS CLI is required but not installed.${NC}"; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed.${NC}"; exit 1; }
    
    # Check AWS credentials
    aws sts get-caller-identity >/dev/null 2>&1 || { echo -e "${RED}❌ AWS credentials not configured.${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}🏗️  Deploying infrastructure...${NC}"
    
    cd infrastructure/terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="aws_region=$AWS_REGION" -var="environment=$ENVIRONMENT" -var="domain_name=$DOMAIN_NAME"
    
    # Apply deployment
    read -p "Do you want to proceed with infrastructure deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -auto-approve -var="aws_region=$AWS_REGION" -var="environment=$ENVIRONMENT" -var="domain_name=$DOMAIN_NAME"
        echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Infrastructure deployment cancelled${NC}"
        exit 1
    fi
    
    cd ../..
}

# Get instance details
get_instance_info() {
    echo -e "${YELLOW}📡 Getting instance information...${NC}"
    
    cd infrastructure/terraform
    INSTANCE_IP=$(terraform output -raw instance_public_ip)
    INSTANCE_DNS=$(terraform output -raw instance_public_dns)
    DB_ENDPOINT=$(terraform output -raw database_endpoint)
    REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)
    
    echo "Instance IP: $INSTANCE_IP"
    echo "Instance DNS: $INSTANCE_DNS"
    echo "Database Endpoint: $DB_ENDPOINT"
    echo "Redis Endpoint: $REDIS_ENDPOINT"
    
    cd ../..
}

# Deploy application
deploy_application() {
    echo -e "${YELLOW}📦 Deploying application...${NC}"
    
    # Create production environment file
    cat > .env.production << EOF
# Production Environment
NODE_ENV=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql+asyncpg://dprod:${DB_PASSWORD}@${DB_ENDPOINT}:5432/dprod

# Redis Configuration
REDIS_URL=redis://${REDIS_ENDPOINT}:6379

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["https://${DOMAIN_NAME}", "https://*.${DOMAIN_NAME}"]
ALLOWED_HOSTS=["${DOMAIN_NAME}", "*.${DOMAIN_NAME}"]

# Docker Configuration
DOCKER_SOCKET_PATH=/var/run/docker.sock

# File Upload
MAX_FILE_SIZE=104857600
UPLOAD_PATH=/opt/dprod/uploads

# API URLs
API_URL=https://${DOMAIN_NAME}
NEXT_PUBLIC_API_URL=https://${DOMAIN_NAME}

# CLI Configuration
DPROD_API_URL=https://${DOMAIN_NAME}

# URL Generation (Production)
NODE_ENV=production
EOF

    # Copy files to instance
    echo "Copying application files to instance..."
    scp -o StrictHostKeyChecking=no -r . ubuntu@$INSTANCE_IP:/opt/dprod/
    
    # Deploy on instance
    echo "Deploying application on instance..."
    ssh -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << EOF
        cd /opt/dprod
        cp .env.production .env
        docker-compose -f docker-compose.prod.yml down || true
        docker-compose -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.prod.yml up -d
        systemctl restart dprod || true
EOF

    echo -e "${GREEN}✅ Application deployed successfully${NC}"
}

# Setup SSL certificate
setup_ssl() {
    echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
    
    ssh -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << EOF
        # Install certbot if not already installed
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
        
        # Get SSL certificate
        sudo certbot --nginx -d ${DOMAIN_NAME} -d *.${DOMAIN_NAME} --non-interactive --agree-tos --email admin@${DOMAIN_NAME}
        
        # Setup auto-renewal
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
EOF

    echo -e "${GREEN}✅ SSL certificate setup completed${NC}"
}

# Run health checks
health_check() {
    echo -e "${YELLOW}🏥 Running health checks...${NC}"
    
    # Wait for services to start
    echo "Waiting for services to start..."
    sleep 30
    
    # Check API health
    if curl -f http://$INSTANCE_IP/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ API health check passed${NC}"
    else
        echo -e "${RED}❌ API health check failed${NC}"
        return 1
    fi
    
    # Check HTTPS (if SSL is configured)
    if curl -f https://$DOMAIN_NAME/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTPS health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS health check failed (SSL may not be configured yet)${NC}"
    fi
    
    echo -e "${GREEN}✅ Health checks completed${NC}"
}

# Main deployment function
main() {
    check_prerequisites
    deploy_infrastructure
    get_instance_info
    deploy_application
    setup_ssl
    health_check
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}Your Dprod platform is now running at:${NC}"
    echo -e "  HTTP:  http://$INSTANCE_IP"
    echo -e "  HTTPS: https://$DOMAIN_NAME"
    echo -e "  API:   https://$DOMAIN_NAME/api/"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Test the deployment: curl https://$DOMAIN_NAME/health"
    echo "2. Install the CLI: npm install -g dprod-cli"
    echo "3. Login: dprod login -e your@email.com"
    echo "4. Deploy a test project: dprod deploy"
}

# Run main function
main "$@"
