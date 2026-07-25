#!/bin/bash
# CloudGuardian Lambda Deployment Script
# Deploys all 4 Lambda functions to AWS

set -e

LAMBDA_DIR="./lambda-functions"
BUILD_DIR="./build"
REGION="us-east-1"

echo "====================================="
echo "CloudGuardian Lambda Deployment"
echo "====================================="

# Create build directory
mkdir -p $BUILD_DIR

# Function to package Lambda
package_lambda() {
    local function_name=$1
    local source_dir="$LAMBDA_DIR/$function_name"
    local zip_file="$BUILD_DIR/$function_name.zip"
    
    echo ""
    echo "Packaging $function_name..."
    
    # Install dependencies
    if [ -f "$source_dir/requirements.txt" ]; then
        pip install -q -r "$source_dir/requirements.txt" -t "$source_dir/" --upgrade
    fi
    
    # Create zip
    cd "$source_dir"
    zip -q -r "../../$zip_file" . -x "*.pyc" "__pycache__/*" "tests/*"
    cd - > /dev/null
    
    echo "  ✓ Packaged: $zip_file"
}

# Function to deploy Lambda
deploy_lambda() {
    local function_name="cloudguardian-$1"
    local zip_file="$BUILD_DIR/$1.zip"
    
    echo ""
    echo "Deploying $function_name..."
    
    # Check if function exists
    if aws lambda get-function --function-name "$function_name" --region "$REGION" 2>/dev/null; then
        # Update existing function
        aws lambda update-function-code \
            --function-name "$function_name" \
            --zip-file "fileb://$zip_file" \
            --region "$REGION"
        echo "  ✓ Updated function: $function_name"
    else
        echo "  ⚠ Function doesn't exist. Deploy via Terraform first:"
        echo "    cd terraform && terraform apply"
    fi
}

# Package all functions
echo ""
echo "Packaging Lambda functions..."
package_lambda "remediate-s3-public-access"
package_lambda "remediate-iam-mfa"
package_lambda "remediate-ebs-encryption"
package_lambda "remediate-security-group"

# Deploy all functions
echo ""
echo "Deploying Lambda functions..."
deploy_lambda "remediate-s3-public-access"
deploy_lambda "remediate-iam-mfa"
deploy_lambda "remediate-ebs-encryption"
deploy_lambda "remediate-security-group"

echo ""
echo "====================================="
echo "✓ Lambda Deployment Complete!"
echo "====================================="
echo ""
echo "Deployed functions:"
echo "  1. cloudguardian-remediate-s3-public-access"
echo "  2. cloudguardian-remediate-iam-mfa"
echo "  3. cloudguardian-remediate-ebs-encryption"
echo "  4. cloudguardian-remediate-security-group"
echo ""
echo "Next steps:"
echo "  1. Verify deployment: aws lambda list-functions --region $REGION"
echo "  2. Test manually: aws lambda invoke --function-name cloudguardian-remediate-s3-public-access ..."
echo "  3. Monitor CloudWatch Logs: aws logs tail /aws/lambda/cloudguardian-remediate-s3-public-access --follow"
echo ""
