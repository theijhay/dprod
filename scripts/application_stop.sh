#!/bin/bash
set -e

echo "🛑 Stopping Dprod application"

cd /home/ubuntu/dprod

# Stop Docker containers
echo "🛑 Stopping Docker containers..."
sudo docker-compose -f docker-compose.prod.yml down || true

# Stop Nginx
echo "🌐 Stopping Nginx..."
sudo systemctl stop nginx || true

echo "✅ Dprod application stopped successfully"
