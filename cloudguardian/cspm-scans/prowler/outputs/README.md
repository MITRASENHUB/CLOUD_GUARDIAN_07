# Prowler Scan Outputs

This directory contains outputs from Prowler CSPM scans.

## Output Files

### Baseline Scan
- `Baseline_Posture_Prowler.html` - User-provided baseline scan report (HTML)
- `prowler-output.json` - Full scan results in JSON format
- `prowler-output.csv` - Scan results in CSV format
- `prowler-output-ocsf.json` - OCSF normalized format

### Scan Details
- **Scanner**: Prowler 4.0+
- **Target**: AWS Account 782700525901 (Cloud_Guard)
- **Compliance Frameworks**: ISO 27001:2022, HIPAA, PCI-DSS v4.0
- **Severity Levels**: Critical, High, Medium, Low, Informational

## Upload Instructions

**Please upload your `Baseline_Posture_Prowler.html` file here.**

If you need to generate a new scan:
```bash
cd ..
bash run-prowler-scan.sh
```

## File Formats

### JSON Format
Machine-readable format for programmatic processing and consolidation.

### CSV Format
Spreadsheet-compatible format for manual review and filtering.

### HTML Format
Human-readable dashboard with charts, graphs, and detailed findings.

### OCSF Format
Open Cybersecurity Schema Framework - standardized security event format.

## Retention

Scan outputs are gitignored by default to avoid repository bloat. Only summary reports should be committed.
