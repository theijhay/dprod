# ECS Fargate Staging Environment - Simplified
# =============================================

# ECR Repositories for Docker Images
resource "aws_ecr_repository" "dprod_api" {
  name                 = "dprod-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "dprod_orchestrator" {
  name                 = "dprod-orchestrator"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "dprod_detection" {
  name                 = "dprod-detection"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "dprod_staging" {
  name = "dprod-staging"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "dprod_staging" {
  cluster_name = aws_ecs_cluster.dprod_staging.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "dprod-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "dprod-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ECS Task Role Policy for ECR access
resource "aws_iam_role_policy" "ecs_task_ecr_policy" {
  name = "dprod-ecs-task-ecr-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Create new VPC for ECS
resource "aws_vpc" "ecs_vpc" {
  cidr_block           = "10.2.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "dprod-ecs-vpc"
    Environment = "staging"
    Project     = "dprod"
  }
}

# Create Internet Gateway
resource "aws_internet_gateway" "ecs_igw" {
  vpc_id = aws_vpc.ecs_vpc.id

  tags = {
    Name        = "dprod-ecs-igw"
    Environment = "staging"
    Project     = "dprod"
  }
}

# Create public subnets
resource "aws_subnet" "ecs_public_1" {
  vpc_id                  = aws_vpc.ecs_vpc.id
  cidr_block              = "10.2.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "dprod-ecs-public-1"
    Environment = "staging"
    Project     = "dprod"
  }
}

resource "aws_subnet" "ecs_public_2" {
  vpc_id                  = aws_vpc.ecs_vpc.id
  cidr_block              = "10.2.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name        = "dprod-ecs-public-2"
    Environment = "staging"
    Project     = "dprod"
  }
}

# Create route table
resource "aws_route_table" "ecs_public" {
  vpc_id = aws_vpc.ecs_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.ecs_igw.id
  }

  tags = {
    Name        = "dprod-ecs-public-rt"
    Environment = "staging"
    Project     = "dprod"
  }
}

# Associate subnets with route table
resource "aws_route_table_association" "ecs_public_1" {
  subnet_id      = aws_subnet.ecs_public_1.id
  route_table_id = aws_route_table.ecs_public.id
}

resource "aws_route_table_association" "ecs_public_2" {
  subnet_id      = aws_subnet.ecs_public_2.id
  route_table_id = aws_route_table.ecs_public.id
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name_prefix = "dprod-ecs-tasks-"
  vpc_id      = aws_vpc.ecs_vpc.id

  ingress {
    from_port   = 8000
    to_port     = 8002
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.ecs_vpc.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "dprod-ecs-tasks"
    Environment = "staging"
    Project     = "dprod"
  }
}

# Application Load Balancer
resource "aws_lb" "dprod_staging" {
  name               = "dprod-staging-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.ecs_public_1.id, aws_subnet.ecs_public_2.id]

  enable_deletion_protection = false

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

# ALB Security Group
resource "aws_security_group" "alb" {
  name_prefix = "dprod-staging-alb-"
  vpc_id      = aws_vpc.ecs_vpc.id

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

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "dprod-staging-alb"
    Environment = "staging"
    Project     = "dprod"
  }
}

# ALB Target Group for API
resource "aws_lb_target_group" "api" {
  name        = "dprod-staging-api"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.ecs_vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

# ALB Listener
resource "aws_lb_listener" "dprod_staging" {
  load_balancer_arn = aws_lb.dprod_staging.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "dprod_staging" {
  name              = "/ecs/dprod-staging"
  retention_in_days = 7

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

# ECS Task Definition for API (simplified - no database connections for now)
resource "aws_ecs_task_definition" "api" {
  family                   = "dprod-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.dprod_api.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NODE_ENV"
          value = "staging"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/dprod-staging"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

# ECS Service for API
resource "aws_ecs_service" "api" {
  name            = "dprod-api"
  cluster         = aws_ecs_cluster.dprod_staging.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = [aws_subnet.ecs_public_1.id, aws_subnet.ecs_public_2.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.dprod_staging]

  tags = {
    Environment = "staging"
    Project     = "dprod"
  }
}

