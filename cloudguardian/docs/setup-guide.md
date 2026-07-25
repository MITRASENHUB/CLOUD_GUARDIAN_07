# CloudGuardian Setup Guide

## Prerequisites

- **AWS Account**: Cloud_Guard (782700525901) - Already configured
- **Python**: 3.9+
- **Operating System**: Linux (Ubuntu 20.04+) or macOS
- **Hardware**: 8GB RAM minimum, 20GB free disk space

## Quick Setup (Automated)

```bash
cd cloudguardian
bash scripts/setup-environment.sh
```

This installs:
- Python 3.9+
- AWS CLI
- Terraform 1.7+
- Prowler CSPM
- Steampipe with AWS mods
- Python dependencies

## Manual Setup

### Step 1: Install Python and Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.9 python3-pip python3-venv

# macOS
brew install python@3.9

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Install AWS CLI

```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# macOS
brew install awscli
```

### Step 3: Configure AWS Credentials

```bash
aws configure
# AWS Access Key ID: [Your key]
# AWS Secret Access Key: [Your secret]
# Default region: us-east-1
# Default output format: json

# Verify
aws sts get-caller-identity
# Should return account ID: 782700525901
```

### Step 4: Install Terraform

```bash
# Linux
wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
unzip terraform_1.7.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# macOS
brew install terraform

# Verify
terraform version
```

### Step 5: Install CSPM Tools

#### Prowler
```bash
pip install prowler
prowler --version
```

#### Steampipe
```bash
sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"
steampipe plugin install aws
steampipe mod install github.com/turbot/steampipe-mod-aws-compliance
```

#### ScoutSuite (Optional)
```bash
pip install scoutsuite
```

### Step 6: Configure Emergent Universal LLM Key

The Emergent Universal LLM Key is automatically available in your environment. No manual configuration needed.

## Verification

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check AWS
aws --version
aws sts get-caller-identity

# Check Terraform
terraform version

# Check Prowler
prowler --version

# Check Steampipe
steampipe --version

# Check Python packages
python3 -c "import pandas, sklearn, boto3; print('All ML packages OK')"
```

## Directory Setup

```bash
cd cloudguardian

# Create required directories
mkdir -p cspm-scans/prowler/outputs
mkdir -p cspm-scans/steampipe/outputs
mkdir -p ml-prioritization/models
mkdir -p ml-prioritization/data
mkdir -p llm-remediation/outputs
mkdir -p llm-remediation/inputs
mkdir -p compliance/reports
mkdir -p reports
```

## Configuration Files

### AWS Configuration
Edit `config/aws-config.yaml`:
- Set region (default: us-east-1)
- Set account ID (already set: 782700525901)

### Terraform Variables
Copy example file:
```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit as needed
```

## Common Issues

### Issue 1: AWS Credentials Not Working
```bash
# Verify credentials
aws sts get-caller-identity

# If failed, reconfigure
aws configure
```

### Issue 2: Terraform Provider Error
```bash
# Clean and re-init
rm -rf .terraform .terraform.lock.hcl
terraform init
```

### Issue 3: Python Package Conflicts
```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Prowler Not Finding AWS Credentials
```bash
export AWS_PROFILE=default
export AWS_REGION=us-east-1
prowler aws
```

### Issue 5: Steampipe Connection Error
```bash
# Reconnect AWS plugin
steampipe plugin update aws

# Verify connection
steampipe query "select * from aws_account limit 1"
```

## Next Steps

After setup, run the full pipeline:

```bash
# 1. Deploy infrastructure
cd infrastructure
terraform init
terraform apply

# 2. Run CSPM scans
cd ../cspm-scans/prowler
bash run-prowler-scan.sh

cd ../steampipe
bash run-steampipe-scan.sh

# 3. Consolidate findings
cd ../consolidated
python consolidate-findings.py

# 4. Train ML model
cd ../../ml-prioritization
python src/train_model.py
python src/predict.py

# 5. Generate LLM guidance
cd ../llm-remediation
python src/generate_guidance.py

# 6. Deploy Lambda functions
cd ../auto-remediation
bash deploy-lambda.sh

# 7. Generate compliance reports
cd ../compliance
python generate-compliance-report.py
```

Or use the automated script:
```bash
cd cloudguardian
bash scripts/run-full-pipeline.sh
```

## Costs

**AWS Free Tier Coverage**:
- EC2: 750 hours t2.micro/month
- RDS: 750 hours db.t2.micro/month
- S3: 5 GB storage
- Lambda: 1M requests/month
- CloudWatch Logs: 5 GB
- CloudTrail: Free management events

**Emergent Universal LLM Key**: Free

**Expected Monthly Cost**: $0 (within Free Tier limits)

## Cleanup

To avoid AWS charges:

```bash
cd cloudguardian/infrastructure
terraform destroy

# Verify all resources deleted
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId'
aws s3 ls
aws rds describe-db-instances
```

## Support

- Documentation: `docs/`
- Issues: GitHub Issues
- Team Contact: See README.md

---

**Setup Time**: 30-45 minutes  
**Difficulty**: Intermediate  
**Team Size**: 4 members can work in parallel
