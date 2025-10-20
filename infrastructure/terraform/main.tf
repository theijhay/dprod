# Dprod AWS Infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables are defined in variables.tf

# VPC and Networking
resource "aws_vpc" "dprod_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "dprod-vpc"
  }
}

resource "aws_internet_gateway" "dprod_igw" {
  vpc_id = aws_vpc.dprod_vpc.id

  tags = {
    Name = "dprod-igw"
  }
}

resource "aws_subnet" "dprod_public_1" {
  vpc_id                  = aws_vpc.dprod_vpc.id
  cidr_block              = "10.0.10.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "dprod-public-subnet-1"
  }
}

resource "aws_subnet" "dprod_public_2" {
  vpc_id                  = aws_vpc.dprod_vpc.id
  cidr_block              = "10.0.20.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "dprod-public-subnet-2"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_route_table" "dprod_public" {
  vpc_id = aws_vpc.dprod_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.dprod_igw.id
  }

  tags = {
    Name = "dprod-public-rt"
  }
}

resource "aws_route_table_association" "dprod_public_1" {
  subnet_id      = aws_subnet.dprod_public_1.id
  route_table_id = aws_route_table.dprod_public.id
}

resource "aws_route_table_association" "dprod_public_2" {
  subnet_id      = aws_subnet.dprod_public_2.id
  route_table_id = aws_route_table.dprod_public.id
}

# Security Groups
resource "aws_security_group" "dprod_web" {
  name_prefix = "dprod-web-"
  vpc_id      = aws_vpc.dprod_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "dprod-web-sg"
  }
}

resource "aws_security_group" "dprod_internal" {
  name_prefix = "dprod-internal-"
  vpc_id      = aws_vpc.dprod_vpc.id

  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "dprod-internal-sg"
  }
}

# RDS Database
resource "aws_db_subnet_group" "dprod" {
  name       = "dprod-db-subnet-group"
  subnet_ids = [aws_subnet.dprod_public_1.id, aws_subnet.dprod_public_2.id]

  tags = {
    Name = "dprod-db-subnet-group"
  }
}

resource "aws_db_instance" "dprod_postgres" {
  identifier = "dprod-postgres"

  engine         = "postgres"
  engine_version = "15.14"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  db_name  = "dprod"
  username = "dprod"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.dprod_internal.id]
  db_subnet_group_name   = aws_db_subnet_group.dprod.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "dprod-postgres"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "dprod" {
  name       = "dprod-cache-subnet"
  subnet_ids = [aws_subnet.dprod_public_1.id, aws_subnet.dprod_public_2.id]
}

resource "aws_elasticache_cluster" "dprod_redis" {
  cluster_id           = "dprod-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.dprod.name
  security_group_ids   = [aws_security_group.dprod_internal.id]

  tags = {
    Name = "dprod-redis"
  }
}

# EC2 Instance
resource "aws_instance" "dprod_server" {
  ami                    = local.ubuntu_ami_id
  instance_type          = "t3.medium"
  key_name               = aws_key_pair.dprod.key_name
  vpc_security_group_ids = [aws_security_group.dprod_web.id, aws_security_group.dprod_internal.id]
  subnet_id              = aws_subnet.dprod_public_1.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    db_endpoint = aws_db_instance.dprod_postgres.endpoint
    redis_endpoint = aws_elasticache_cluster.dprod_redis.cache_nodes[0].address
    domain_name = var.domain_name
    db_password = var.db_password
  }))

  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
  }

  tags = {
    Name = "dprod-server"
  }
}

# Key Pair
resource "aws_key_pair" "dprod" {
  key_name   = "dprod-key"
  public_key = file("/home/dev-soft/.ssh/id_rsa.pub")
}

# Use a known working Ubuntu 22.04 LTS AMI for us-east-1
# This AMI ID is stable and widely available
locals {
  ubuntu_ami_id = "ami-0c02fb55956c7d316"  # Ubuntu 22.04 LTS in us-east-1
}

# Outputs
output "instance_public_ip" {
  value = aws_instance.dprod_server.public_ip
}

output "instance_public_dns" {
  value = aws_instance.dprod_server.public_dns
}

output "database_endpoint" {
  value = aws_db_instance.dprod_postgres.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.dprod_redis.cache_nodes[0].address
}
