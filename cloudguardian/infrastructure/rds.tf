# RDS MySQL Database Configuration

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-db-subnet-group"
    }
  )
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${local.name_prefix}-mysql-params"
  family = "mysql8.0"
  
  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }
  
  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
  
  tags = local.common_tags
}

# RDS MySQL Instance
resource "aws_db_instance" "main" {
  identifier             = "${local.name_prefix}-mysql-${random_id.suffix.hex}"
  engine                 = "mysql"
  engine_version         = var.rds_engine_version
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  storage_type           = "gp3"
  
  db_name  = var.rds_database_name
  username = var.rds_username
  password = random_password.rds_password.result
  
  # MISCONFIGURATION 6: Publicly accessible RDS
  publicly_accessible = var.misconfig_rds_public_access ? true : false
  
  # MISCONFIGURATION 7: Automated backups disabled
  backup_retention_period = 0  # Should be 7 days minimum
  
  # MISCONFIGURATION 8: Storage not encrypted
  storage_encrypted = var.misconfig_disable_encryption ? false : true
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  
  skip_final_snapshot       = true
  final_snapshot_identifier = null
  
  # Performance Insights disabled to stay in Free Tier
  enabled_cloudwatch_logs_exports = []
  
  tags = merge(
    local.common_tags,
    {
      Name                = "${local.name_prefix}-mysql"
      Misconfiguration    = "Public Access, No Backups, Unencrypted"
      MisconfigurationID  = "RDS-001"
    }
  )
}

# Store RDS password in SSM Parameter Store
resource "aws_ssm_parameter" "rds_password" {
  name        = "/${var.project_name}/${var.environment}/rds/master-password"
  description = "RDS MySQL master password"
  type        = "SecureString"
  value       = random_password.rds_password.result
  
  tags = local.common_tags
}
