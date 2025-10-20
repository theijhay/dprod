#!/bin/bash
set -e

echo "🚀 Starting Dprod application"

cd /home/ubuntu/dprod

# Stop any existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose -f docker-compose.prod.yml down || true

# Pull latest images
echo "📥 Pulling latest images..."
sudo docker-compose -f docker-compose.prod.yml pull

# Build and start services
echo "🏗️  Building and starting services..."
sudo docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
sudo docker-compose -f docker-compose.prod.yml ps

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp /home/ubuntu/dprod/infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp /home/ubuntu/dprod/infrastructure/nginx/conf.d/dprod.conf /etc/nginx/conf.d/dprod.conf
sudo cp /home/ubuntu/dprod/infrastructure/nginx/conf.d/locations.conf /etc/nginx/conf.d/locations.conf

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Dprod application started successfully"
echo "🌐 Application should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
