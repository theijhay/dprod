variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (production, staging, etc.)"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for Dprod platform"
  type        = string
  default     = "dprod.app"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Secret key for JWT tokens"
  type        = string
  sensitive   = true
  default     = "your-secret-key-change-this"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}
