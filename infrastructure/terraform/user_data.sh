#!/bin/bash

# Dprod Server Setup Script
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install nginx
apt-get install -y nginx certbot python3-certbot-nginx

# Install Node.js (for CLI)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Python and Poetry
apt-get install -y python3 python3-pip
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"

# Create dprod user
useradd -m -s /bin/bash dprod
usermod -aG docker dprod

# Create application directory
mkdir -p /opt/dprod
chown dprod:dprod /opt/dprod

# Clone repository (you'll need to update this with your actual repo)
cd /opt/dprod
# git clone https://github.com/yourusername/dprod.git .

# Create environment file
cat > /opt/dprod/.env << EOF
# Production Environment
NODE_ENV=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql+asyncpg://dprod:${db_password}@${db_endpoint}:5432/dprod

# Redis Configuration
REDIS_URL=redis://${redis_endpoint}:6379

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=["https://${domain_name}", "https://*.${domain_name}"]
ALLOWED_HOSTS=["${domain_name}", "*.${domain_name}"]

# Docker Configuration
DOCKER_SOCKET_PATH=/var/run/docker.sock

# File Upload
MAX_FILE_SIZE=104857600
UPLOAD_PATH=/opt/dprod/uploads

# API URLs
API_URL=https://${domain_name}
NEXT_PUBLIC_API_URL=https://${domain_name}

# CLI Configuration
DPROD_API_URL=https://${domain_name}

# URL Generation (Production)
NODE_ENV=production
EOF

# Create nginx configuration
cat > /etc/nginx/sites-available/dprod << EOF
server {
    listen 80;
    server_name ${domain_name} *.${domain_name};
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${domain_name} *.${domain_name};
    
    # SSL configuration (will be set up by certbot)
    ssl_certificate /etc/letsencrypt/live/${domain_name}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${domain_name}/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files
    location /static/ {
        alias /opt/dprod/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
    
    # Default location
    location / {
        return 200 'Dprod Platform is running!';
        add_header Content-Type text/plain;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/dprod /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Start nginx
systemctl enable nginx
systemctl start nginx

# Create systemd service for Dprod
cat > /etc/systemd/system/dprod.service << EOF
[Unit]
Description=Dprod Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/dprod
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=dprod
Group=dprod

[Install]
WantedBy=multi-user.target
EOF

# Enable Dprod service
systemctl enable dprod

# Create log rotation
cat > /etc/logrotate.d/dprod << EOF
/opt/dprod/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 dprod dprod
}
EOF

# Set up log directory
mkdir -p /opt/dprod/logs
chown dprod:dprod /opt/dprod/logs

# Create uploads directory
mkdir -p /opt/dprod/uploads
chown dprod:dprod /opt/dprod/uploads

# Install monitoring tools
apt-get install -y htop iotop nethogs

# Set up log monitoring
cat > /opt/dprod/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script
while true; do
    echo "$(date): Dprod Status Check" >> /opt/dprod/logs/monitor.log
    docker ps >> /opt/dprod/logs/monitor.log
    echo "---" >> /opt/dprod/logs/monitor.log
    sleep 300  # Check every 5 minutes
done
EOF

chmod +x /opt/dprod/monitor.sh

# Create startup script
cat > /opt/dprod/start.sh << 'EOF'
#!/bin/bash
cd /opt/dprod
export PATH="/root/.local/bin:$PATH"
docker-compose up -d
EOF

chmod +x /opt/dprod/start.sh

# Set proper permissions
chown -R dprod:dprod /opt/dprod

echo "Dprod server setup completed!"
echo "Next steps:"
echo "1. Clone your repository to /opt/dprod"
echo "2. Run: certbot --nginx -d ${domain_name}"
echo "3. Start Dprod: systemctl start dprod"
