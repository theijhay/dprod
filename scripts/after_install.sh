#!/bin/bash
set -e

echo "🚀 Starting Dprod deployment - After Install"

# Set proper permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/dprod
sudo chmod -R 755 /home/ubuntu/dprod

# Make scripts executable
sudo chmod +x /home/ubuntu/dprod/scripts/*.sh

# Copy environment template if production env doesn't exist
if [ ! -f /home/ubuntu/dprod/.env.production ]; then
    echo "📝 Creating production environment file..."
    cp /home/ubuntu/dprod/infrastructure/env.production.template /home/ubuntu/dprod/.env.production
    echo "⚠️  Please update .env.production with your actual values"
fi

# Create necessary directories
sudo mkdir -p /home/ubuntu/dprod/infrastructure/nginx/conf.d
sudo mkdir -p /home/ubuntu/dprod/infrastructure/fluent-bit
sudo mkdir -p /tmp/dprod/uploads

# Set permissions for uploads directory
sudo chown -R ubuntu:ubuntu /tmp/dprod
sudo chmod -R 755 /tmp/dprod

echo "✅ After Install completed successfully"
