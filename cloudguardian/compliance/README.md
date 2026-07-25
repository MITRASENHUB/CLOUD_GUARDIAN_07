# CloudGuardian Compliance Mapping

This directory contains compliance framework mappings for security findings.

## Supported Frameworks

### 1. ISO 27001:2022
- **File**: `mappings/iso27001-crosswalk.csv`
- **Standard**: Information Security Management
- **Controls**: Annex A (93 controls)
- **Focus**: Information security governance, risk management

### 2. DPDP Act 2023 (India)
- **File**: `mappings/dpdp-crosswalk.csv`
- **Standard**: Digital Personal Data Protection Act 2023
- **Focus**: Data protection, privacy, consent management

### 3. HIPAA Security Rule
- **File**: `mappings/hipaa-crosswalk.csv`
- **Standard**: Health Insurance Portability and Accountability Act
- **Focus**: Protected Health Information (PHI) security

### 4. PCI-DSS v4.0
- **File**: `mappings/pci-dss-crosswalk.csv`
- **Standard**: Payment Card Industry Data Security Standard
- **Focus**: Cardholder data protection

## Crosswalk Structure

Each crosswalk CSV contains:
- `finding_check_id` - CSPM check identifier
- `framework` - Compliance framework name
- `control_id` - Framework control ID
- `control_title` - Control description
- `requirement` - Specific requirement text
- `mapping_strength` - Direct, Partial, or Indirect
- `notes` - Additional context

## Existing Files to Upload

**Please upload these files to `mappings/` directory:**
1. `AWS_Steampipe_ISO27001_Mapping.xlsx`
2. `AWS_Cloud_Vulnerability_Control_Register_ISO27001_DPDP2023.xlsx`

## Generate Compliance Report

```bash
python generate-compliance-report.py
```

Outputs:
- `reports/compliance-report.md` - Human-readable report
- `reports/iso27001-assessment.pdf` - ISO 27001 assessment
- `reports/gap-analysis.xlsx` - Gap analysis spreadsheet

## Compliance Summary

Example output:
```
ISO 27001:2022 Compliance: 67%
- Compliant: 42 controls
- Non-compliant: 28 controls
- Not applicable: 23 controls

Top Gaps:
1. A.8.24 - Use of cryptography (6 findings)
2. A.8.20 - Networks controls (4 findings)
3. A.5.15 - Access control (3 findings)
```

## Team Responsibilities

**Team Mode (4 members)**: Each member maps one framework
- Member 1: ISO 27001:2022
- Member 2: DPDP Act 2023
- Member 3: HIPAA
- Member 4: PCI-DSS v4.0

**Status**: Placeholder structure created. Upload existing Excel files and create CSV crosswalks.
