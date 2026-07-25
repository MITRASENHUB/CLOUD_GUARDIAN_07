# Steampipe Scan Outputs

This directory contains outputs from Steampipe compliance benchmarks.

## Output Files

- `steampipe-findings.csv` - Compliance check results
- `steampipe-iso27001.csv` - ISO 27001:2022 benchmark results
- `steampipe-hipaa.csv` - HIPAA compliance results
- `steampipe-pci-dss.csv` - PCI-DSS v4.0 results

## Scan Details
- **Tool**: Steampipe with AWS Compliance mods
- **Target**: AWS Account 782700525901 (Cloud_Guard)
- **Benchmarks**: ISO 27001:2022, HIPAA, PCI-DSS v4.0

## Usage

```bash
cd ..
bash run-steampipe-scan.sh
```

## Steampipe Advantages

- SQL-based security queries
- Real-time AWS API queries
- Customizable compliance checks
- Integration with PostgreSQL ecosystem

## Output Format

CSV columns:
- control_id
- control_title
- status (pass/fail/skip)
- resource
- reason
- severity
