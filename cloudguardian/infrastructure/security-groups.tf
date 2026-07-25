# Security Groups Configuration

# Web Tier Security Group
resource "aws_security_group" "web" {
  name        = "${local.name_prefix}-web-sg"
  description = "Security group for web tier instances"
  vpc_id      = aws_vpc.main.id
  
  # MISCONFIGURATION 1: SSH from anywhere (0.0.0.0/0)
  ingress {
    description = "SSH from anywhere - MISCONFIGURED"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.misconfig_sg_open_ssh ? ["0.0.0.0/0"] : [var.vpc_cidr]
  }
  
  # MISCONFIGURATION 2: HTTP from anywhere
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # MISCONFIGURATION 3: HTTPS from anywhere
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound traffic
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    local.common_tags,
    {
      Name                = "${local.name_prefix}-web-sg"
      Misconfiguration    = "SSH from 0.0.0.0/0"
      MisconfigurationID  = "SG-001"
    }
  )
}

# Database Security Group
resource "aws_security_group" "database" {
  name        = "${local.name_prefix}-db-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id
  
  # MISCONFIGURATION 4: MySQL port from anywhere (if RDS is public)
  ingress {
    description = "MySQL from anywhere - MISCONFIGURED"
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = var.misconfig_rds_public_access ? ["0.0.0.0/0"] : [var.vpc_cidr]
  }
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    local.common_tags,
    {
      Name                = "${local.name_prefix}-db-sg"
      Misconfiguration    = "MySQL from 0.0.0.0/0"
      MisconfigurationID  = "SG-002"
    }
  )
}

# Lambda Security Group
resource "aws_security_group" "lambda" {
  name        = "${local.name_prefix}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id
  
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-lambda-sg"
    }
  )
}
