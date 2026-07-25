# EventBridge Rules for CloudGuardian Lambda Triggers

# Event Rule: S3 Bucket Created/Modified
resource "aws_cloudwatch_event_rule" "s3_bucket_events" {
  name        = "cloudguardian-s3-bucket-events"
  description = "Trigger S3 remediation on bucket creation/policy changes"
  
  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["s3.amazonaws.com"]
      eventName = [
        "CreateBucket",
        "PutBucketAcl",
        "PutBucketPolicy",
        "DeleteBucketPolicy",
        "PutPublicAccessBlock"
      ]
    }
  })
  
  tags = {
    Project = "CloudGuardian"
  }
}

resource "aws_cloudwatch_event_target" "s3_remediation" {
  rule      = aws_cloudwatch_event_rule.s3_bucket_events.name
  target_id = "S3RemediationLambda"
  arn       = aws_lambda_function.remediate_s3_public_access.arn
}

resource "aws_lambda_permission" "allow_eventbridge_s3" {
  statement_id  = "AllowEventBridgeInvokeS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remediate_s3_public_access.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_bucket_events.arn
}

# Event Rule: IAM User Console Login
resource "aws_cloudwatch_event_rule" "iam_login_events" {
  name        = "cloudguardian-iam-login-events"
  description = "Trigger MFA enforcement on IAM user console login"
  
  event_pattern = jsonencode({
    source      = ["aws.signin"]
    detail-type = ["AWS Console Sign In via CloudTrail"]
    detail = {
      eventName = ["ConsoleLogin"]
      userIdentity = {
        type = ["IAMUser"]
      }
    }
  })
  
  tags = {
    Project = "CloudGuardian"
  }
}

resource "aws_cloudwatch_event_target" "iam_mfa_remediation" {
  rule      = aws_cloudwatch_event_rule.iam_login_events.name
  target_id = "IAMMFARemediationLambda"
  arn       = aws_lambda_function.remediate_iam_mfa.arn
}

resource "aws_lambda_permission" "allow_eventbridge_iam" {
  statement_id  = "AllowEventBridgeInvokeIAM"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.remediate_iam_mfa.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.iam_login_events.arn
}

# Event Rule: EBS Volume Creation
resource "aws_cloudwatch_event_rule" "ebs_volume_events" {
  name        = "cloudguardian-ebs-volume-events"
  description = "Trigger EBS encryption check on volume creation"
  
  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["EBS Volume Notification"]
    detail = {
      event = ["createVolume"]
    }
  })
  
  tags = {
    Project = "CloudGuardian"
  }
}

resource "aws_cloudwatch_event_target" "ebs_remediation" {
  rule      = aws_cloudwatch_event_rule.ebs_volume_events.name
  target_id = "EBSRemediationLambda"
  arn       = aws_lambda_function.remediate_ebs_encryption.arn
}

# Event Rule: Security Group Modification
resource "aws_cloudwatch_event_rule" "sg_modification_events" {
  name        = "cloudguardian-sg-modification-events"
  description = "Trigger SG hardening on security group rule changes"
  
  event_pattern = jsonencode({
    source      = ["aws.ec2"]
    detail-type = ["AWS API Call via CloudTrail"]
    detail = {
      eventSource = ["ec2.amazonaws.com"]
      eventName = [
        "AuthorizeSecurityGroupIngress",
        "CreateSecurityGroup"
      ]
    }
  })
  
  tags = {
    Project = "CloudGuardian"
  }
}

resource "aws_cloudwatch_event_target" "sg_remediation" {
  rule      = aws_cloudwatch_event_rule.sg_modification_events.name
  target_id = "SGRemediationLambda"
  arn       = aws_lambda_function.remediate_security_group.arn
}

# Scheduled scan (daily at 2 AM UTC)
resource "aws_cloudwatch_event_rule" "daily_scan" {
  name                = "cloudguardian-daily-scan"
  description         = "Trigger daily comprehensive security scan"
  schedule_expression = "cron(0 2 * * ? *)"
  
  tags = {
    Project = "CloudGuardian"
  }
}
