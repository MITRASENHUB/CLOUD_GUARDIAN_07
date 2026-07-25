# CloudGuardian Auto-Remediation System

## Overview

Automated remediation system using AWS Lambda functions with safety guardrails.

## Lambda Functions (Team Mode: 4 Functions)

### 1. S3 Public Access Remediation
**File**: `lambda-functions/remediate-s3-public-access/handler.py`
**Trigger**: EventBridge rule on S3 bucket creation/modification
**Action**: Automatically block public access on S3 buckets
**Guardrails**:
- Check if bucket is in approved exception list
- Verify bucket is not used for static website hosting
- Send SNS notification before remediation
- Log all actions to CloudWatch

### 2. IAM MFA Enforcement
**File**: `lambda-functions/remediate-iam-mfa/handler.py`
**Trigger**: EventBridge rule on IAM user console login without MFA
**Action**: Attach MFA requirement policy to IAM user
**Guardrails**:
- Exclude emergency break-glass accounts
- Grace period of 7 days for new users
- Send email notification to user
- Require manager approval for enforcement

### 3. EBS Encryption Enablement
**File**: `lambda-functions/remediate-ebs-encryption/handler.py`
**Trigger**: EventBridge rule on unencrypted EBS volume creation
**Action**: Enable encryption by default for the account/region
**Guardrails**:
- Only affect new volumes (cannot encrypt existing without snapshot)
- Check for performance-sensitive workloads
- Verify KMS key availability
- Send notification to resource owner

### 4. Security Group Hardening
**File**: `lambda-functions/remediate-security-group/handler.py`
**Trigger**: EventBridge rule on security group rule modification
**Action**: Remove overly permissive rules (0.0.0.0/0 on sensitive ports)
**Guardrails**:
- Whitelist approved public-facing services
- Check for active connections before removal
- Backup original rules
- Rollback capability

## Deployment

### Prerequisites
```bash
# Install AWS SAM CLI
pip install aws-sam-cli

# Install dependencies
cd lambda-functions/remediate-s3-public-access
pip install -r requirements.txt -t .
```

### Deploy All Functions
```bash
# Use deployment script
bash deploy-lambda.sh

# Or use Terraform
cd terraform
terraform init
terraform apply
```

## Safety Guardrails

### Pre-Remediation Checks
- Resource ownership verification
- Business hours validation
- Impact assessment
- Exception list checking

### Post-Remediation Verification
- Confirm desired state achieved
- Check for unintended side effects
- Verify service availability
- Update CMDB/tracking systems

### Approval Workflow
- Critical resources require manual approval
- Auto-approve for low-risk changes
- Notification sent to resource owners
- Audit trail in CloudTrail

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Invoke locally
sam local invoke RemediateS3PublicAccess --event events/s3-public.json
```

## Monitoring

- CloudWatch Logs for execution logs
- CloudWatch Metrics for success/failure rates
- SNS notifications for critical actions
- CloudWatch Alarms for anomalies

## Rollback

All functions support rollback:
```bash
# Rollback S3 remediation
aws lambda invoke \
  --function-name cloudguardian-remediate-s3 \
  --payload '{"action": "rollback", "resource": "bucket-name"}' \
  response.json
```

## Cost

**Estimated Monthly Cost**: $0-5
- Lambda: 1M requests free tier
- EventBridge: Minimal cost
- CloudWatch Logs: < $1/month

## Files to Create

### For Each Lambda Function:
1. `handler.py` - Main Lambda function code
2. `requirements.txt` - Python dependencies
3. `README.md` - Function-specific documentation
4. `tests/` - Unit and integration tests
5. `events/` - Sample test events

### Shared:
1. `guardrails/pre_checks.py` - Pre-remediation validation
2. `guardrails/post_checks.py` - Post-remediation verification
3. `guardrails/approval_workflow.py` - Human approval workflow
4. `terraform/lambda-deployment.tf` - Infrastructure deployment
5. `deploy-lambda.sh` - Deployment automation

**Status**: Placeholder structure created. Implementation pending.
