#!/bin/bash
# Run Prowler CSPM Scan
# AWS Account: Cloud_Guard (782700525901)

set -e

echo "===================================="
echo "CloudGuardian Prowler Scan"
echo "===================================="

# Check if Prowler is installed
if ! command -v prowler &> /dev/null; then
    echo "Prowler not found. Installing..."
    pip install prowler
fi

echo ""
echo "Scanning AWS Account: 782700525901 (Cloud_Guard)"
echo "Region: us-east-1"
echo ""

# Set output directory
OUTPUT_DIR="./outputs"
mkdir -p $OUTPUT_DIR

# Run Prowler scan
echo "Running Prowler scan..."
prowler aws \
  --output-formats json csv html json-ocsf \
  --output-directory $OUTPUT_DIR \
  --output-filename prowler-output \
  --compliance iso27001_2022 hipaa pci_dss_v4_0 \
  --severity critical high medium low \
  --status FAIL PASS WARNING \
  --region us-east-1

echo ""
echo "✓ Prowler scan complete!"
echo "Output files:"
ls -lh $OUTPUT_DIR/prowler-output*
echo ""
echo "Next steps:"
echo "  1. Review HTML report: $OUTPUT_DIR/prowler-output.html"
echo "  2. Run consolidation: cd ../consolidated && python consolidate-findings.py"
echo ""
