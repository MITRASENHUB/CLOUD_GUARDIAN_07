# CloudTrail Configuration

# MISCONFIGURATION 15: CloudTrail with minimal logging
resource "aws_cloudtrail" "main" {
  name                          = "${local.name_prefix}-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = false  # Should be true
  enable_logging                = true
  
  # Log file validation disabled (should be enabled)
  enable_log_file_validation = false
  
  # No CloudWatch Logs integration (should be enabled)
  # cloud_watch_logs_group_arn = aws_cloudwatch_log_group.cloudtrail.arn
  # cloud_watch_logs_role_arn  = aws_iam_role.cloudtrail_cloudwatch.arn
  
  event_selector {
    read_write_type           = "All"
    include_management_events = true
    
    # Data events not configured (should include S3 and Lambda)
  }
  
  tags = merge(
    local.common_tags,
    {
      Name                = "${local.name_prefix}-cloudtrail"
      Misconfiguration    = "Single region, no log validation, no CloudWatch"
      MisconfigurationID  = "TRAIL-001"
    }
  )
  
  depends_on = [aws_s3_bucket_policy.cloudtrail]
}
