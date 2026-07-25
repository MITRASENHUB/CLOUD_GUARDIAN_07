# Placeholder Files to Upload

This document lists the existing files you mentioned that need to be uploaded to complete the project.

## Files to Upload

### 1. Project Guide
**Location**: `/app/cloudguardian/docs/project-guide/`

Upload:
- `05_CSE_Capstone_CloudGuardian.pdf` - Original project guide from your professor

### 2. Existing Reports
**Location**: `/app/cloudguardian/reports/`

Upload:
- `Baseline_Posture_Prowler.html` - Existing Prowler baseline scan
- `Prowler_Misconfigs.xlsx` - Prowler misconfigurations spreadsheet

### 3. Compliance Mappings (Excel)
**Location**: `/app/cloudguardian/compliance/mappings/`

Upload:
- `AWS_Steampipe_ISO27001_Mapping.xlsx` - Existing ISO 27001 mapping
- `AWS_Cloud_Vulnerability_Control_Register_ISO27001_DPDP2023.xlsx` - Control register

### 4. Prowler Scan Outputs
**Location**: `/app/cloudguardian/cspm-scans/prowler/outputs/`

Upload:
- `Baseline_Posture_Prowler.html` - Baseline Prowler scan HTML

## How to Upload

### Option 1: Via File Explorer/Terminal
```bash
# Copy files from local machine
cp /path/to/your/files/*.pdf /app/cloudguardian/docs/project-guide/
cp /path/to/your/files/*.html /app/cloudguardian/reports/
cp /path/to/your/files/*.xlsx /app/cloudguardian/reports/
cp /path/to/your/files/*.xlsx /app/cloudguardian/compliance/mappings/
```

### Option 2: Via Web Interface
Use the file upload feature to upload files to their respective directories.

## Verification

After upload, verify files exist:
```bash
ls -la /app/cloudguardian/docs/project-guide/
ls -la /app/cloudguardian/reports/
ls -la /app/cloudguardian/compliance/mappings/
ls -la /app/cloudguardian/cspm-scans/prowler/outputs/
```

## Once Uploaded

After uploading these files, you can:

1. **Process existing Prowler HTML report**:
   ```bash
   # Parse HTML for findings
   python cspm-scans/prowler/parse-html-report.py
   ```

2. **Import ISO 27001 mappings**:
   ```bash
   # Convert Excel to CSV
   python compliance/import-xlsx-mappings.py
   ```

3. **Analyze baseline findings**:
   ```bash
   # Compare baseline vs current
   python reports/baseline-comparison.py
   ```

## Notes

- These files are your original work and cannot be regenerated automatically
- Placeholders have been created in the correct locations
- Once uploaded, the pipeline can use them directly
- Existing scan reports serve as baseline for progress tracking

---

**Status**: Placeholders created. Waiting for file uploads.
