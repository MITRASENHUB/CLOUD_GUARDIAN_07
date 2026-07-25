# CloudGuardian Infrastructure (Terraform)

This directory contains Terraform Infrastructure as Code (IaC) for deploying the CloudGuardian AWS workload with **intentional misconfigurations** for security testing.

## 🛠️ Architecture

### Components
- **VPC**: Custom VPC with public/private subnets
- **EC2**: Web tier instances (t2.micro)
- **RDS**: MySQL database (db.t2.micro)
- **S3**: Storage buckets with various permission levels
- **IAM**: Users, roles, policies
- **Security Groups**: Network access controls
- **CloudTrail**: Audit logging
- **Lambda**: Auto-remediation functions

### Intentional Misconfigurations (Team Mode: 12+)

1. **S3 Bucket Public Access** - S3 bucket with public read/write
2. **IAM Root Account Usage** - Active root account without MFA
3. **Overly Permissive Security Groups** - 0.0.0.0/0 on sensitive ports
4. **Unencrypted EBS Volumes** - EC2 volumes without encryption
5. **RDS Public Access** - Database exposed to internet
6. **IAM Policy Wildcard Permissions** - IAM policies with `*` actions
7. **S3 Bucket Versioning Disabled** - No versioning for critical data
8. **CloudTrail Logging Disabled** - No audit trail
9. **Unencrypted S3 Buckets** - No server-side encryption
10. **IAM Users Without MFA** - Users with console access, no MFA
11. **Security Group SSH from Anywhere** - Port 22 open to 0.0.0.0/0
12. **RDS Automated Backups Disabled** - No backup retention
13. **S3 Bucket Access Logging Disabled** - No access logs
14. **Unused IAM Credentials** - Old access keys not rotated

## 🚀 Deployment

### Prerequisites
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
unzip terraform_1.7.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Configure AWS CLI
aws configure
# AWS Access Key ID: [YOUR_KEY]
# AWS Secret Access Key: [YOUR_SECRET]
# Default region name: us-east-1
# Default output format: json
```

### Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Review execution plan
terraform plan -out=tfplan

# Apply configuration
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

### Inject Misconfigurations
```bash
# Run misconfiguration injection script
cd ../misconfigurations
bash inject-misconfigs.sh
```

## 📝 Configuration Files

- `main.tf` - Main Terraform configuration
- `provider.tf` - AWS provider setup
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `vpc.tf` - VPC and networking
- `ec2.tf` - EC2 instances
- `rds.tf` - RDS database
- `s3.tf` - S3 buckets
- `iam.tf` - IAM resources
- `security-groups.tf` - Security groups
- `cloudtrail.tf` - CloudTrail logging
- `terraform.tfvars.example` - Example variables

## 🛡️ Security Notes

**WARNING**: This infrastructure contains intentional security misconfigurations for educational purposes.

- Deploy only in isolated lab environments
- Do not use in production
- Clean up resources after testing to avoid costs
- Monitor AWS Free Tier usage

## 🧹 Cleanup

```bash
# Destroy all infrastructure
terraform destroy

# Verify deletion
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId'
aws s3 ls
aws rds describe-db-instances
```

## 📊 Cost Estimation

**Free Tier Eligible:**
- EC2: t2.micro (750 hours/month)
- RDS: db.t2.micro (750 hours/month)
- S3: 5GB storage
- Lambda: 1M requests/month

**Estimated Monthly Cost**: $0 (within Free Tier limits)
