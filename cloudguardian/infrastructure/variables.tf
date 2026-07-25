# CloudGuardian Terraform Variables

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "782700525901"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cloudguardian"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "lab"
}

variable "team_size" {
  description = "Number of team members"
  type        = number
  default     = 4
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# EC2 Configuration
variable "ec2_instance_type" {
  description = "EC2 instance type (Free Tier)"
  type        = string
  default     = "t2.micro"
}

variable "ec2_instance_count" {
  description = "Number of EC2 instances"
  type        = number
  default     = 2
}

variable "ec2_ami_id" {
  description = "AMI ID for EC2 instances (Amazon Linux 2023)"
  type        = string
  default     = ""  # Will use data source to fetch latest
}

# RDS Configuration
variable "rds_instance_class" {
  description = "RDS instance class (Free Tier)"
  type        = string
  default     = "db.t2.micro"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_engine_version" {
  description = "MySQL engine version"
  type        = string
  default     = "8.0"
}

variable "rds_database_name" {
  description = "Initial database name"
  type        = string
  default     = "cloudguardian"
}

variable "rds_username" {
  description = "RDS master username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "rds_password" {
  description = "RDS master password"
  type        = string
  default     = ""  # Will be generated
  sensitive   = true
}

# S3 Configuration
variable "s3_bucket_count" {
  description = "Number of S3 buckets to create"
  type        = number
  default     = 3
}

# IAM Configuration
variable "iam_user_count" {
  description = "Number of IAM users to create"
  type        = number
  default     = 4  # One per team member
}

# Tags
variable "additional_tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

# Misconfiguration Flags (for controlled injection)
variable "enable_misconfigurations" {
  description = "Enable intentional misconfigurations"
  type        = bool
  default     = true
}

variable "misconfig_s3_public_access" {
  description = "Make S3 bucket publicly accessible"
  type        = bool
  default     = true
}

variable "misconfig_rds_public_access" {
  description = "Make RDS publicly accessible"
  type        = bool
  default     = true
}

variable "misconfig_sg_open_ssh" {
  description = "Open SSH to 0.0.0.0/0"
  type        = bool
  default     = true
}

variable "misconfig_disable_encryption" {
  description = "Disable encryption for EBS and S3"
  type        = bool
  default     = true
}
