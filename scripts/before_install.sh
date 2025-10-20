#!/bin/bash
set -e

echo "🚀 Starting Dprod deployment - Before Install"

# Update system
sudo apt-get update -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing Nginx..."
    sudo apt-get install -y nginx
fi

# Install Python3 and pip if not present
if ! command -v python3 &> /dev/null; then
    echo "📦 Installing Python3..."
    sudo apt-get install -y python3 python3-pip
fi

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ Before Install completed successfully"
