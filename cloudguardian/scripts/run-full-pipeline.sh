#!/bin/bash
# CloudGuardian Full Pipeline Execution
# Runs the complete detection, prioritization, and remediation pipeline

set -e

PROJECT_ROOT=$(pwd)
LOG_FILE="$PROJECT_ROOT/pipeline-execution.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "=========================================" | tee "$LOG_FILE"
echo "CloudGuardian Full Pipeline Execution" | tee -a "$LOG_FILE"
echo "=========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

START_TIME=$(date +%s)

# Step 1: Verify infrastructure
log "Step 1: Verifying infrastructure deployment..."
cd "$PROJECT_ROOT/infrastructure"
if [ ! -f "terraform.tfstate" ]; then
    log "ERROR: Infrastructure not deployed. Run 'terraform apply' first."
    exit 1
fi
log "✓ Infrastructure verified"
echo "" | tee -a "$LOG_FILE"

# Step 2: Run CSPM scans
log "Step 2: Running CSPM scans..."
cd "$PROJECT_ROOT/cspm-scans"

log "  - Running Prowler scan..."
cd prowler
bash run-prowler-scan.sh >> "$LOG_FILE" 2>&1
log "    ✓ Prowler scan complete"

log "  - Running Steampipe scan..."
cd ../steampipe
bash run-steampipe-scan.sh >> "$LOG_FILE" 2>&1
log "    ✓ Steampipe scan complete"

log "✓ CSPM scans complete"
echo "" | tee -a "$LOG_FILE"

# Step 3: Consolidate findings
log "Step 3: Consolidating findings..."
cd "$PROJECT_ROOT/cspm-scans/consolidated"
python3 consolidate-findings.py >> "$LOG_FILE" 2>&1
log "✓ Findings consolidated"
echo "" | tee -a "$LOG_FILE"

# Step 4: ML risk prioritization
log "Step 4: Running ML risk prioritization..."
cd "$PROJECT_ROOT/ml-prioritization"

if [ ! -f "models/risk_classifier.pkl" ]; then
    log "  - Training ML model (first run)..."
    python3 src/train_model.py >> "$LOG_FILE" 2>&1
    log "    ✓ Model trained"
fi

log "  - Generating risk predictions..."
python3 src/predict.py >> "$LOG_FILE" 2>&1
log "✓ Risk prioritization complete"
echo "" | tee -a "$LOG_FILE"

# Step 5: LLM remediation guidance
log "Step 5: Generating LLM remediation guidance..."
cd "$PROJECT_ROOT/llm-remediation"
python3 src/generate_guidance.py >> "$LOG_FILE" 2>&1
log "✓ Remediation guidance generated"
echo "" | tee -a "$LOG_FILE"

# Step 6: Generate compliance reports
log "Step 6: Generating compliance reports..."
cd "$PROJECT_ROOT/compliance"
if [ -f "generate-compliance-report.py" ]; then
    python3 generate-compliance-report.py >> "$LOG_FILE" 2>&1
    log "✓ Compliance reports generated"
else
    log "⚠ Compliance report script not found, skipping"
fi
echo "" | tee -a "$LOG_FILE"

# Calculate execution time
END_TIME=$(date +%s)
EXECUTION_TIME=$((END_TIME - START_TIME))

log "========================================="
log "✓ Pipeline Execution Complete!"
log "========================================="
log ""
log "Execution time: ${EXECUTION_TIME} seconds"
log ""
log "Outputs:"
log "  - Consolidated findings: cspm-scans/consolidated/consolidated-findings.json"
log "  - Prioritized findings: ml-prioritization/data/prioritized-findings.csv"
log "  - Remediation guidance: llm-remediation/outputs/remediation-guidance.md"
log "  - Compliance reports: compliance/reports/"
log ""
log "Next steps:"
log "  1. Review prioritized findings: cat ml-prioritization/data/prioritized-findings.csv"
log "  2. Review remediation guidance: cat llm-remediation/outputs/remediation-guidance.md"
log "  3. Deploy Lambda functions: cd auto-remediation && bash deploy-lambda.sh"
log "  4. Review compliance reports: ls compliance/reports/"
log ""
