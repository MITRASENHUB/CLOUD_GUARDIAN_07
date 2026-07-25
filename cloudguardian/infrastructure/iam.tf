# IAM Configuration

# IAM Users for Team Members
resource "aws_iam_user" "team_members" {
  count = var.iam_user_count
  name  = "${local.name_prefix}-user-${count.index + 1}"
  
  tags = merge(
    local.common_tags,
    {
      Name = "Team Member ${count.index + 1}"
    }
  )
}

# MISCONFIGURATION 13: IAM access keys without rotation
resource "aws_iam_access_key" "team_members" {
  count = var.iam_user_count
  user  = aws_iam_user.team_members[count.index].name
  
  # These keys will never be rotated (intentional misconfiguration)
}

# MISCONFIGURATION 14: Overly permissive IAM policy with wildcard
resource "aws_iam_policy" "overly_permissive" {
  name        = "${local.name_prefix}-overly-permissive-policy"
  description = "Intentionally overly permissive policy - MISCONFIGURED"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "ec2:*",
          "rds:*"
        ]
        Resource = "*"  # Should be specific resources
      }
    ]
  })
  
  tags = merge(
    local.common_tags,
    {
      Misconfiguration   = "Wildcard permissions"
      MisconfigurationID = "IAM-001"
    }
  )
}

# Attach overly permissive policy to users
resource "aws_iam_user_policy_attachment" "team_members" {
  count      = var.iam_user_count
  user       = aws_iam_user.team_members[count.index].name
  policy_arn = aws_iam_policy.overly_permissive.arn
}

# EC2 Instance Role
resource "aws_iam_role" "ec2_instance" {
  name = "${local.name_prefix}-ec2-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach policies to EC2 role
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2_instance.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "ec2_cloudwatch" {
  role       = aws_iam_role.ec2_instance.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution" {
  name = "${local.name_prefix}-lambda-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = local.common_tags
}

# Lambda basic execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda VPC execution policy
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Lambda remediation policy
resource "aws_iam_policy" "lambda_remediation" {
  name        = "${local.name_prefix}-lambda-remediation-policy"
  description = "Policy for Lambda auto-remediation functions"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutBucketPublicAccessBlock",
          "s3:PutBucketVersioning",
          "s3:PutEncryptionConfiguration",
          "ec2:ModifyInstanceAttribute",
          "ec2:ModifyVolume",
          "rds:ModifyDBInstance",
          "iam:UpdateAccessKey",
          "iam:AttachUserPolicy",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupIngress"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "lambda_remediation" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = aws_iam_policy.lambda_remediation.arn
}
