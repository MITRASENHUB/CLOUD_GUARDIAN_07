#!/bin/bash
# CloudGuardian Environment Setup Script
# Sets up all required tools and dependencies

set -e

echo "====================================="
echo "CloudGuardian Environment Setup"
echo "====================================="
echo ""

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Update package manager
echo "1. Updating package manager..."
if [ "$OS" = "linux" ]; then
    sudo apt-get update -qq
else
    brew update
fi
echo "   ✓ Package manager updated"
echo ""

# Install Python 3.9+
echo "2. Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "   Installing Python 3.9+..."
    if [ "$OS" = "linux" ]; then
        sudo apt-get install -y python3.9 python3-pip python3-venv
    else
        brew install python@3.9
    fi
fi
PYTHON_VERSION=$(python3 --version)
echo "   ✓ $PYTHON_VERSION installed"
echo ""

# Install AWS CLI
echo "3. Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    if [ "$OS" = "linux" ]; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    else
        brew install awscli
    fi
fi
AWS_VERSION=$(aws --version)
echo "   ✓ $AWS_VERSION installed"
echo ""

# Install Terraform
echo "4. Installing Terraform..."
if ! command -v terraform &> /dev/null; then
    if [ "$OS" = "linux" ]; then
        wget -q https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
        unzip -q terraform_1.7.0_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_1.7.0_linux_amd64.zip
    else
        brew install terraform
    fi
fi
TERRAFORM_VERSION=$(terraform version -json | python3 -c "import sys, json; print(json.load(sys.stdin)['terraform_version'])")
echo "   ✓ Terraform $TERRAFORM_VERSION installed"
echo ""

# Install Python packages
echo "5. Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
    echo "   ✓ Python packages installed"
else
    echo "   ⚠ requirements.txt not found, skipping"
fi
echo ""

# Install Prowler
echo "6. Installing Prowler..."
pip3 install -q prowler
echo "   ✓ Prowler installed"
echo ""

# Install Steampipe
echo "7. Installing Steampipe..."
if ! command -v steampipe &> /dev/null; then
    sudo /bin/sh -c "$(curl -fsSL https://steampipe.io/install/steampipe.sh)"
    steampipe plugin install aws
    steampipe mod install steampipe-mod-aws-compliance
fi
echo "   ✓ Steampipe installed"
echo ""

# Install Jupyter
echo "8. Installing Jupyter..."
pip3 install -q jupyter notebook ipykernel
echo "   ✓ Jupyter installed"
echo ""

# Configure AWS CLI
echo "9. Configuring AWS CLI..."
echo "   Please enter your AWS credentials:"
aws configure
echo "   ✓ AWS CLI configured"
echo ""

# Verify installations
echo "====================================="
echo "Installation Verification"
echo "====================================="
echo "Python: $(python3 --version)"
echo "AWS CLI: $(aws --version | cut -d' ' -f1)"
echo "Terraform: $(terraform version -json | python3 -c 'import sys, json; print(json.load(sys.stdin)["terraform_version"])')"
echo "Prowler: $(prowler -v 2>&1 | head -n1)"
echo "Steampipe: $(steampipe -v | head -n1)"
echo "Jupyter: $(jupyter --version | head -n1)"
echo ""

echo "====================================="
echo "✓ Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "  1. Deploy infrastructure: cd infrastructure && terraform apply"
echo "  2. Run CSPM scans: cd cspm-scans && ./run-all-scans.sh"
echo "  3. Train ML model: cd ml-prioritization && python src/train_model.py"
echo "  4. Generate LLM guidance: cd llm-remediation && python src/generate_guidance.py"
echo ""
