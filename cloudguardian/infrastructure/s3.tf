# S3 Buckets Configuration

# Data Buckets
resource "aws_s3_bucket" "data" {
  count  = var.s3_bucket_count
  bucket = "${local.name_prefix}-data-${count.index + 1}-${random_id.suffix.hex}"
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-data-bucket-${count.index + 1}"
    }
  )
}

# MISCONFIGURATION 9: Public access block disabled on first bucket
resource "aws_s3_bucket_public_access_block" "data" {
  count  = var.s3_bucket_count
  bucket = aws_s3_bucket.data[count.index].id
  
  # First bucket is misconfigured with public access
  block_public_acls       = count.index == 0 && var.misconfig_s3_public_access ? false : true
  block_public_policy     = count.index == 0 && var.misconfig_s3_public_access ? false : true
  ignore_public_acls      = count.index == 0 && var.misconfig_s3_public_access ? false : true
  restrict_public_buckets = count.index == 0 && var.misconfig_s3_public_access ? false : true
}

# MISCONFIGURATION 10: Versioning disabled
resource "aws_s3_bucket_versioning" "data" {
  count  = var.s3_bucket_count
  bucket = aws_s3_bucket.data[count.index].id
  
  versioning_configuration {
    status = "Disabled"  # Should be "Enabled"
  }
}

# MISCONFIGURATION 11: Server-side encryption disabled on first bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  count  = var.s3_bucket_count
  bucket = aws_s3_bucket.data[count.index].id
  
  # Only encrypt buckets 2 and 3, leave bucket 1 unencrypted
  dynamic "rule" {
    for_each = (count.index > 0 || !var.misconfig_disable_encryption) ? [1] : []
    
    content {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# MISCONFIGURATION 12: Access logging disabled
resource "aws_s3_bucket_logging" "data" {
  count  = 0  # Disabled - should be enabled for all buckets
  bucket = aws_s3_bucket.data[count.index].id
  
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "access-logs/bucket-${count.index}/"
}

# Log bucket (properly configured)
resource "aws_s3_bucket" "logs" {
  bucket = "${local.name_prefix}-logs-${random_id.suffix.hex}"
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-logs-bucket"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudTrail S3 Bucket
resource "aws_s3_bucket" "cloudtrail" {
  bucket = "${local.name_prefix}-cloudtrail-${random_id.suffix.hex}"
  
  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-cloudtrail-bucket"
    }
  )
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudTrail bucket policy
resource "aws_s3_bucket_policy" "cloudtrail" {
  bucket = aws_s3_bucket.cloudtrail.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail.arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail.arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}
