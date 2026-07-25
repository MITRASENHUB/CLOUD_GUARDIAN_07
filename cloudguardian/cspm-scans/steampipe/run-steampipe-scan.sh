#!/bin/bash
# Run Steampipe CSPM Scan
# AWS Account: Cloud_Guard (782700525901)

set -e

echo "===================================="
echo "CloudGuardian Steampipe Scan"
echo "===================================="

# Check if Steampipe is installed
if ! command -v steampipe &> /dev/null; then
    echo "Steampipe not found. Installing..."
    
    # Install Steampipe
    curl -s https://steampipe.io/install/steampipe.sh | sh
    
    # Install AWS plugin and compliance mods
    steampipe plugin install aws
    steampipe mod install steampipe-mod-aws-compliance
fi

echo ""
echo "Scanning AWS Account: 782700525901 (Cloud_Guard)"
echo "Region: us-east-1"
echo ""

# Set output directory
OUTPUT_DIR="./outputs"
mkdir -p $OUTPUT_DIR

echo "Running Steampipe compliance benchmarks..."

# Run ISO 27001:2022 benchmark
echo "1/3 Running ISO 27001:2022 benchmark..."
steampipe check aws_compliance.benchmark.iso27001_2022 \
  --export $OUTPUT_DIR/steampipe-iso27001.csv

# Run HIPAA benchmark
echo "2/3 Running HIPAA benchmark..."
steampipe check aws_compliance.benchmark.hipaa_security_rule_2003 \
  --export $OUTPUT_DIR/steampipe-hipaa.csv

# Run PCI-DSS benchmark
echo "3/3 Running PCI-DSS v4.0 benchmark..."
steampipe check aws_compliance.benchmark.pci_dss_v4_0 \
  --export $OUTPUT_DIR/steampipe-pci-dss.csv

# Combine all results
echo ""
echo "Consolidating results..."
cat $OUTPUT_DIR/steampipe-*.csv > $OUTPUT_DIR/steampipe-findings.csv

echo ""
echo "✓ Steampipe scan complete!"
echo "Output files:"
ls -lh $OUTPUT_DIR/steampipe-*.csv
echo ""
echo "Next steps:"
echo "  1. Review findings: cat $OUTPUT_DIR/steampipe-findings.csv"
echo "  2. Run consolidation: cd ../consolidated && python consolidate-findings.py"
echo ""
