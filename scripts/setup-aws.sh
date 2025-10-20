#!/bin/bash

# AWS Setup Script for Dprod
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up AWS for Dprod deployment${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}📦 Installing AWS CLI...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    else
        echo -e "${RED}❌ Unsupported operating system. Please install AWS CLI manually.${NC}"
        exit 1
    fi
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Terraform...${NC}"
    
    # Detect OS and architecture
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ $(uname -m) == "x86_64" ]]; then
            TERRAFORM_ARCH="linux_amd64"
        else
            TERRAFORM_ARCH="linux_arm64"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ $(uname -m) == "arm64" ]]; then
            TERRAFORM_ARCH="darwin_arm64"
        else
            TERRAFORM_ARCH="darwin_amd64"
        fi
    else
        echo -e "${RED}❌ Unsupported operating system. Please install Terraform manually.${NC}"
        exit 1
    fi
    
    # Download and install Terraform
    TERRAFORM_VERSION="1.6.0"
    wget "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_${TERRAFORM_ARCH}.zip"
    unzip "terraform_${TERRAFORM_VERSION}_${TERRAFORM_ARCH}.zip"
    sudo mv terraform /usr/local/bin/
    rm "terraform_${TERRAFORM_VERSION}_${TERRAFORM_ARCH}.zip"
fi

# Configure AWS credentials
echo -e "${YELLOW}🔑 Configuring AWS credentials...${NC}"
echo "Please provide your AWS credentials:"

read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo
read -p "AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Configure AWS CLI
aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
aws configure set default.region $AWS_REGION
aws configure set default.output json

# Test AWS connection
echo -e "${YELLOW}🧪 Testing AWS connection...${NC}"
if aws sts get-caller-identity >/dev/null 2>&1; then
    echo -e "${GREEN}✅ AWS credentials configured successfully${NC}"
else
    echo -e "${RED}❌ Failed to connect to AWS. Please check your credentials.${NC}"
    exit 1
fi

# Create SSH key pair if it doesn't exist
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}🔐 Creating SSH key pair...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}✅ SSH key pair created${NC}"
else
    echo -e "${GREEN}✅ SSH key pair already exists${NC}"
fi

# Create S3 bucket for Terraform state (optional but recommended)
echo -e "${YELLOW}🪣 Setting up S3 bucket for Terraform state...${NC}"
BUCKET_NAME="dprod-terraform-state-$(date +%s)"
aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION

# Create Terraform backend configuration
cat > infrastructure/terraform/backend.tf << EOF
terraform {
  backend "s3" {
    bucket = "$BUCKET_NAME"
    key    = "dprod/terraform.tfstate"
    region = "$AWS_REGION"
  }
}
EOF

echo -e "${GREEN}✅ S3 bucket created: $BUCKET_NAME${NC}"

# Create environment file
cat > .env.aws << EOF
# AWS Configuration
AWS_REGION=$AWS_REGION
ENVIRONMENT=production
DOMAIN_NAME=dprod.app

# Database password (change this!)
DB_PASSWORD=$(openssl rand -base64 32)

# S3 Bucket
TERRAFORM_BUCKET=$BUCKET_NAME
EOF

echo -e "${GREEN}✅ AWS setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the configuration in .env.aws"
echo "2. Update the domain name if needed"
echo "3. Run: ./scripts/deploy.sh"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "- Keep your AWS credentials secure"
echo "- The database password is in .env.aws - keep it safe!"
echo "- The S3 bucket $BUCKET_NAME stores your Terraform state"
