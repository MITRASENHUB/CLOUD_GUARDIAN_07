# CloudGuardian Terraform Outputs

# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

# EC2 Outputs
output "ec2_instance_ids" {
  description = "EC2 instance IDs"
  value       = aws_instance.web[*].id
}

output "ec2_public_ips" {
  description = "EC2 public IP addresses"
  value       = aws_instance.web[*].public_ip
}

output "ec2_private_ips" {
  description = "EC2 private IP addresses"
  value       = aws_instance.web[*].private_ip
}

# RDS Outputs
output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}

output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# S3 Outputs
output "s3_bucket_names" {
  description = "S3 bucket names"
  value       = aws_s3_bucket.data[*].id
}

output "s3_bucket_arns" {
  description = "S3 bucket ARNs"
  value       = aws_s3_bucket.data[*].arn
}

# IAM Outputs
output "iam_user_names" {
  description = "IAM user names"
  value       = aws_iam_user.team_members[*].name
}

output "iam_role_arns" {
  description = "IAM role ARNs"
  value       = {
    lambda_execution = aws_iam_role.lambda_execution.arn
    ec2_instance     = aws_iam_role.ec2_instance.arn
  }
}

# Security Group Outputs
output "security_group_ids" {
  description = "Security group IDs"
  value       = {
    web      = aws_security_group.web.id
    database = aws_security_group.database.id
    lambda   = aws_security_group.lambda.id
  }
}

# Misconfiguration Summary
output "misconfiguration_summary" {
  description = "Summary of intentional misconfigurations"
  value = {
    s3_public_access        = var.misconfig_s3_public_access
    rds_public_access       = var.misconfig_rds_public_access
    sg_open_ssh             = var.misconfig_sg_open_ssh
    encryption_disabled     = var.misconfig_disable_encryption
    total_misconfigs        = "12+"
  }
}

# CloudTrail Output
output "cloudtrail_name" {
  description = "CloudTrail trail name"
  value       = aws_cloudtrail.main.name
}

output "cloudtrail_s3_bucket" {
  description = "CloudTrail S3 bucket"
  value       = aws_s3_bucket.cloudtrail.id
}

# Region Info
output "deployment_region" {
  description = "Deployment AWS region"
  value       = var.aws_region
}

output "account_id" {
  description = "AWS Account ID"
  value       = var.aws_account_id
}
