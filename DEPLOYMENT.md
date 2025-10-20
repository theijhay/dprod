# Dprod Deployment Guide

This guide covers deploying Dprod to AWS using CodeDeploy.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **GitHub Repository** with your code
3. **AWS CLI** configured with credentials
4. **Terraform** installed (for infrastructure)

## Infrastructure Setup

### 1. Deploy Infrastructure

```bash
# Navigate to infrastructure directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply -var="db_password=YOUR_SECURE_PASSWORD"
```

This creates:
- VPC with 2 subnets across different AZs
- RDS PostgreSQL database
- ElastiCache Redis cluster
- EC2 instance with proper security groups
- IAM roles for CodeDeploy

### 2. Configure Environment Variables

Copy the environment template and update with your values:

```bash
cp infrastructure/env.production.template .env.production
# Edit .env.production with your actual database and Redis endpoints
```

## CodeDeploy Setup

### 1. Create CodeDeploy Application

```bash
aws deploy create-application \
    --application-name dprod-app \
    --compute-platform Server
```

### 2. Create Deployment Group

```bash
aws deploy create-deployment-group \
    --application-name dprod-app \
    --deployment-group-name dprod-deployment-group \
    --service-role-arn arn:aws:iam::YOUR_ACCOUNT:role/CodeDeployServiceRole \
    --ec2-tag-filters Type=KEY_AND_VALUE,Key=Name,Value=dprod-server
```

### 3. Create IAM Role for CodeDeploy

Create a role with the following policies:
- `AWSCodeDeployRole`
- `AmazonEC2FullAccess`
- `AmazonS3FullAccess`

## Deployment Process

### 1. Push to GitHub

```bash
git add .
git commit -m "Deploy to AWS"
git push origin main
```

### 2. Create Deployment

```bash
aws deploy create-deployment \
    --application-name dprod-app \
    --deployment-group-name dprod-deployment-group \
    --github-location repository=YOUR_USERNAME/dprod,commitId=COMMIT_HASH
```

### 3. Monitor Deployment

```bash
aws deploy get-deployment --deployment-id DEPLOYMENT_ID
```

## Manual Deployment (Alternative)

If CodeDeploy is not available, you can deploy manually:

1. **Connect to EC2 instance** via AWS Console
2. **Clone repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dprod.git
   cd dprod
   ```
3. **Configure environment**:
   ```bash
   cp infrastructure/env.production.template .env.production
   # Edit .env.production with your values
   ```
4. **Deploy application**:
   ```bash
   sudo docker-compose -f docker-compose.prod.yml up -d --build
   ```

## Environment Variables

### Required for Production

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key
- `API_URL`: Public API URL
- `DPROD_DOMAIN`: Your domain name

### Optional

- `DEBUG`: Set to `false` for production
- `NODE_ENV`: Set to `production`
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ALLOWED_HOSTS`: Allowed hostnames

## Troubleshooting

### Check Application Logs

```bash
# Docker logs
sudo docker-compose -f docker-compose.prod.yml logs

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Check Service Status

```bash
# Docker services
sudo docker-compose -f docker-compose.prod.yml ps

# Nginx status
sudo systemctl status nginx
```

### Common Issues

1. **Database Connection**: Verify `DATABASE_URL` is correct
2. **Redis Connection**: Verify `REDIS_URL` is correct
3. **Port Conflicts**: Ensure ports 80, 443, 8000 are available
4. **Permissions**: Check file permissions and ownership

## Security Notes

- Never commit `.env` files to version control
- Use strong passwords for database
- Enable SSL/TLS in production
- Regularly update dependencies
- Monitor application logs

## Support

For issues and questions:
- Check application logs
- Verify environment variables
- Test database and Redis connectivity
- Review AWS CloudWatch logs