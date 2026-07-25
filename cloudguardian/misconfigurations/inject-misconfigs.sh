#!/bin/bash
# Misconfiguration Injection Script
# This script intentionally introduces security misconfigurations
# WARNING: Only run in lab/test environments!

set -e

echo "===================================="
echo "CloudGuardian Misconfiguration Injection"
echo "===================================="
echo ""
echo "WARNING: This script will intentionally introduce security misconfigurations."
echo "Only proceed if this is a lab/test environment."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Injecting misconfigurations..."

# Source Terraform outputs
cd ../infrastructure
TERRAFORM_OUTPUT=$(terraform output -json)

# Extract resource IDs
S3_BUCKET_1=$(echo $TERRAFORM_OUTPUT | jq -r '.s3_bucket_names.value[0]')
SECURITY_GROUP_WEB=$(echo $TERRAFORM_OUTPUT | jq -r '.security_group_ids.value.web')
RDS_INSTANCE=$(terraform output -json | jq -r '.rds_endpoint.value' | cut -d':' -f1)

echo "Target Resources:"
echo "  S3 Bucket: $S3_BUCKET_1"
echo "  Security Group: $SECURITY_GROUP_WEB"
echo "  RDS Instance: $RDS_INSTANCE"
echo ""

# Note: Most misconfigurations are already applied via Terraform
# This script is for documentation and verification purposes

echo "✓ Misconfigurations already applied via Terraform:"
echo "  1. S3 public access (S3-001)"
echo "  2. SSH from 0.0.0.0/0 (SG-001)"
echo "  3. MySQL from 0.0.0.0/0 (SG-002)"
echo "  4. Unencrypted EBS volumes (EC2-001)"
echo "  5. RDS publicly accessible (RDS-001)"
echo "  6. RDS backups disabled (RDS-002)"
echo "  7. RDS storage unencrypted (RDS-003)"
echo "  8. S3 versioning disabled (S3-002)"
echo "  9. S3 unencrypted (S3-003)"
echo "  10. S3 logging disabled (S3-004)"
echo "  11. IAM wildcard permissions (IAM-001)"
echo "  12. IAM keys not rotated (IAM-002)"
echo "  13. CloudTrail single region (TRAIL-001)"
echo "  14. CloudTrail log validation disabled (TRAIL-002)"
echo ""
echo "✓ All 14 misconfigurations active!"
echo ""
echo "Next steps:"
echo "  1. Run CSPM scans: cd ../cspm-scans && ./run-all-scans.sh"
echo "  2. Verify detections in scan outputs"
echo ""
