#!/bin/bash
set -e

echo "🚀 Deploying Dprod to AWS using CodeDeploy"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current commit hash
COMMIT_HASH=$(git rev-parse HEAD)
echo "📝 Using commit: $COMMIT_HASH"

# Check if CodeDeploy application exists
if ! aws deploy get-application --application-name dprod-app &> /dev/null; then
    echo "❌ CodeDeploy application 'dprod-app' not found."
    echo "Please create it in AWS Console first:"
    echo "1. Go to AWS CodeDeploy Console"
    echo "2. Create application 'dprod-app'"
    echo "3. Create deployment group 'dprod-deployment-group'"
    exit 1
fi

# Create deployment
echo "🚀 Creating deployment..."
DEPLOYMENT_ID=$(aws deploy create-deployment \
    --application-name dprod-app \
    --deployment-group-name dprod-deployment-group \
    --github-location repository=theijhay/dprod,commitId=$COMMIT_HASH \
    --query 'deploymentId' \
    --output text)

echo "✅ Deployment created: $DEPLOYMENT_ID"
echo "🔍 Monitor progress at: https://us-east-1.console.aws.amazon.com/codesuite/codedeploy/applications/dprod-app/deployment-groups/dprod-deployment-group/deployments/$DEPLOYMENT_ID"

# Wait for deployment to complete (optional)
read -p "Do you want to wait for deployment to complete? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⏳ Waiting for deployment to complete..."
    aws deploy wait deployment-successful --deployment-id $DEPLOYMENT_ID
    echo "✅ Deployment completed successfully!"
else
    echo "📋 Deployment started. Check the AWS Console for progress."
fi
