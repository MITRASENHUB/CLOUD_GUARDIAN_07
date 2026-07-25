# Lambda Function Deployment (Terraform)

# S3 Public Access Remediation Lambda
resource "aws_lambda_function" "remediate_s3_public_access" {
  filename         = "${path.module}/../lambda-functions/remediate-s3-public-access.zip"
  function_name    = "cloudguardian-remediate-s3-public-access"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 256
  
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.cloudguardian_alerts.arn
      LOG_LEVEL     = "INFO"
    }
  }
  
  tags = {
    Project     = "CloudGuardian"
    Function    = "S3 Public Access Remediation"
    Environment = "lab"
  }
}

# IAM MFA Enforcement Lambda
resource "aws_lambda_function" "remediate_iam_mfa" {
  filename         = "${path.module}/../lambda-functions/remediate-iam-mfa.zip"
  function_name    = "cloudguardian-remediate-iam-mfa"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 256
  
  environment {
    variables = {
      SNS_TOPIC_ARN     = aws_sns_topic.cloudguardian_alerts.arn
      GRACE_PERIOD_DAYS = "7"
    }
  }
  
  tags = {
    Project  = "CloudGuardian"
    Function = "IAM MFA Enforcement"
  }
}

# EBS Encryption Lambda
resource "aws_lambda_function" "remediate_ebs_encryption" {
  filename         = "${path.module}/../lambda-functions/remediate-ebs-encryption.zip"
  function_name    = "cloudguardian-remediate-ebs-encryption"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"
  timeout          = 120
  memory_size      = 512
  
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.cloudguardian_alerts.arn
    }
  }
  
  tags = {
    Project  = "CloudGuardian"
    Function = "EBS Encryption Remediation"
  }
}

# Security Group Hardening Lambda
resource "aws_lambda_function" "remediate_security_group" {
  filename         = "${path.module}/../lambda-functions/remediate-security-group.zip"
  function_name    = "cloudguardian-remediate-security-group"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 256
  
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.cloudguardian_alerts.arn
    }
  }
  
  tags = {
    Project  = "CloudGuardian"
    Function = "Security Group Hardening"
  }
}

# SNS Topic for alerts
resource "aws_sns_topic" "cloudguardian_alerts" {
  name = "cloudguardian-alerts"
  
  tags = {
    Project = "CloudGuardian"
  }
}

# DynamoDB Table for approval workflow
resource "aws_dynamodb_table" "approvals" {
  name           = "cloudguardian-approvals"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "approval_id"
  
  attribute {
    name = "approval_id"
    type = "S"
  }
  
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  tags = {
    Project = "CloudGuardian"
  }
}
