# CloudGuardian Main Terraform Configuration

# Data source for latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Random password for RDS
resource "random_password" "rds_password" {
  length  = 16
  special = true
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# Local variables
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Team        = "CSPM-Team"
    TeamSize    = tostring(var.team_size)
  }
}
