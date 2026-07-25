#!/usr/bin/env python3
"""
CloudGuardian Compliance Report Generator
Generates compliance reports mapping findings to ISO 27001, DPDP, HIPAA, PCI-DSS
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Paths
MAPPINGS_DIR = Path("./mappings")
REPORTS_DIR = Path("./reports")
FINDINGS_PATH = Path("../cspm-scans/consolidated/consolidated-findings.json")

REPORTS_DIR.mkdir(exist_ok=True)


def load_findings() -> pd.DataFrame:
    """Load consolidated findings"""
    if not FINDINGS_PATH.exists():
        print(f"Warning: Findings not found at {FINDINGS_PATH}")
        return pd.DataFrame()
    
    with open(FINDINGS_PATH, 'r') as f:
        findings = json.load(f)
    
    return pd.DataFrame(findings)


def load_mappings() -> Dict[str, pd.DataFrame]:
    """Load all compliance mappings"""
    mappings = {}
    
    for framework_file in MAPPINGS_DIR.glob("*-crosswalk.csv"):
        framework = framework_file.stem.replace("-crosswalk", "").replace("-", "_")
        mappings[framework] = pd.read_csv(framework_file)
        print(f"Loaded {len(mappings[framework])} mappings for {framework}")
    
    return mappings


def calculate_compliance_score(findings: pd.DataFrame, mappings: pd.DataFrame) -> Dict:
    """
    Calculate compliance score for a framework
    
    Score = (Passing controls / Total mapped controls) * 100
    """
    if findings.empty or mappings.empty:
        return {'score': 0, 'compliant': 0, 'non_compliant': 0, 'total_controls': 0}
    
    # Get unique controls from mappings
    total_controls = mappings['control_id'].nunique()
    
    # Find non-compliant controls (controls with FAIL findings)
    finding_checks = set(findings[findings['status'] == 'FAIL']['check_id'].tolist())
    mapping_checks = set(mappings['finding_check_id'].tolist())
    
    failing_checks = finding_checks.intersection(mapping_checks)
    non_compliant_controls = mappings[mappings['finding_check_id'].isin(failing_checks)]['control_id'].nunique()
    
    compliant_controls = total_controls - non_compliant_controls
    
    score = (compliant_controls / total_controls * 100) if total_controls > 0 else 0
    
    return {
        'score': round(score, 1),
        'compliant': compliant_controls,
        'non_compliant': non_compliant_controls,
        'total_controls': total_controls,
        'failing_checks': list(failing_checks)
    }


def generate_gap_analysis(findings: pd.DataFrame, mappings: pd.DataFrame) -> pd.DataFrame:
    """Generate gap analysis for a framework"""
    if findings.empty or mappings.empty:
        return pd.DataFrame()
    
    # Merge findings with mappings
    finding_checks = findings[findings['status'] == 'FAIL'][['check_id', 'severity', 'resource']].rename(
        columns={'check_id': 'finding_check_id'}
    )
    
    gap = mappings.merge(finding_checks, on='finding_check_id', how='left')
    gap['status'] = gap['severity'].apply(
        lambda x: 'Non-Compliant' if pd.notna(x) else 'Compliant'
    )
    
    return gap


def generate_markdown_report(all_results: Dict, output_path: Path):
    """Generate comprehensive Markdown compliance report"""
    md_content = f"""# CloudGuardian Compliance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**AWS Account**: Cloud_Guard (782700525901)  
**Team**: CloudGuardian CSPM Team (4 members)

---

## Executive Summary

CloudGuardian assessed the AWS infrastructure against four major compliance frameworks:

| Framework | Score | Compliant | Non-Compliant | Total Controls |
|-----------|-------|-----------|---------------|----------------|
"""
    
    for framework, result in all_results.items():
        framework_display = framework.replace('_', ' ').upper()
        md_content += f"| {framework_display} | {result['score']}% | {result['compliant']} | {result['non_compliant']} | {result['total_controls']} |\n"
    
    md_content += "\n---\n\n## Detailed Framework Analysis\n\n"
    
    for framework, result in all_results.items():
        framework_display = framework.replace('_', ' ').upper()
        md_content += f"""### {framework_display}

**Compliance Score**: {result['score']}%  
**Compliant Controls**: {result['compliant']} / {result['total_controls']}  
**Non-Compliant Controls**: {result['non_compliant']}

#### Top Failing Checks
"""
        
        failing_checks = result.get('failing_checks', [])[:5]
        if failing_checks:
            for check in failing_checks:
                md_content += f"- `{check}`\n"
        else:
            md_content += "- No failing checks detected\n"
        
        md_content += "\n"
    
    md_content += """
---

## Compliance Improvement Recommendations

### Priority 1: Address Critical Non-Compliance
1. Enable S3 bucket public access blocking (all frameworks)
2. Enable encryption at rest (S3, EBS, RDS)
3. Restrict security group rules
4. Enable MFA for all users

### Priority 2: Enhance Audit Capabilities
1. Enable CloudTrail multi-region logging
2. Enable log file validation
3. Enable S3 access logging
4. Enable RDS automated backups

### Priority 3: Access Control
1. Implement least privilege IAM policies
2. Rotate access keys regularly
3. Remove wildcard permissions
4. Enable MFA enforcement

---

## Framework-Specific Guidance

### ISO 27001:2022
Focus on Annex A controls A.5 (Access Control), A.8.20-A.8.24 (Networks and Cryptography), and A.8.13-A.8.15 (Backup, Logging).

### DPDP Act 2023 (India)
Section 8 (Security Safeguards) is the primary control. Focus on encryption, access controls, and breach notification capabilities.

### HIPAA Security Rule
Focus on 164.312 (Technical Safeguards): Access Control, Audit Controls, Integrity, Person/Entity Authentication, Transmission Security.

### PCI-DSS v4.0
Focus on Requirements 1 (Network Security), 3 (Data Protection), 7 (Access Control), 8 (Authentication), and 10 (Logging and Monitoring).

---

## Compliance Roadmap

### Month 1: Critical Fixes
- Block public S3 access
- Enable encryption everywhere
- Restrict security groups
- Enable MFA

### Month 2: Audit and Monitoring
- Configure CloudTrail properly
- Enable comprehensive logging
- Set up alerting

### Month 3: Access Control Refinement
- Implement least privilege
- Rotate credentials
- Regular access reviews

### Ongoing: Continuous Compliance
- Automated CSPM scans
- Lambda-based remediation
- Quarterly compliance assessments

---

**Report Generated by**: CloudGuardian Compliance Report Generator  
**Version**: 1.0  
**Contact**: CloudGuardian Team (4 members)
"""
    
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    print(f"✓ Markdown report saved to {output_path}")


def generate_excel_gap_analysis(all_gaps: Dict, output_path: Path):
    """Generate Excel gap analysis with multiple sheets"""
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for framework, gap_df in all_gaps.items():
                if not gap_df.empty:
                    framework_display = framework.replace('_', ' ').upper()[:30]
                    gap_df.to_excel(writer, sheet_name=framework_display, index=False)
        
        print(f"✓ Excel gap analysis saved to {output_path}")
    except Exception as e:
        print(f"Warning: Failed to create Excel file: {e}")


def main():
    print("=" * 60)
    print("CloudGuardian Compliance Report Generator")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading findings and mappings...")
    findings = load_findings()
    print(f"   Loaded {len(findings)} findings")
    
    mappings = load_mappings()
    print(f"   Loaded {len(mappings)} framework mappings")
    
    # Calculate compliance for each framework
    print("\n2. Calculating compliance scores...")
    all_results = {}
    all_gaps = {}
    
    for framework, mapping_df in mappings.items():
        result = calculate_compliance_score(findings, mapping_df)
        all_results[framework] = result
        
        gap = generate_gap_analysis(findings, mapping_df)
        all_gaps[framework] = gap
        
        print(f"   {framework}: {result['score']}% ({result['compliant']}/{result['total_controls']})")
    
    # Generate reports
    print("\n3. Generating reports...")
    
    # Markdown report
    md_path = REPORTS_DIR / "compliance-report.md"
    generate_markdown_report(all_results, md_path)
    
    # Excel gap analysis
    excel_path = REPORTS_DIR / "gap-analysis.xlsx"
    generate_excel_gap_analysis(all_gaps, excel_path)
    
    # JSON summary
    summary_path = REPORTS_DIR / "compliance-summary.json"
    with open(summary_path, 'w') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'account_id': '782700525901',
            'frameworks': all_results
        }, f, indent=2)
    print(f"✓ JSON summary saved to {summary_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Compliance Report Summary")
    print("=" * 60)
    for framework, result in all_results.items():
        framework_display = framework.replace('_', ' ').upper()
        print(f"{framework_display:20} {result['score']:5}% ({result['compliant']:3}/{result['total_controls']:3} controls)")
    
    print(f"\n✓ Reports generated in {REPORTS_DIR}/")
    print("\nFiles generated:")
    print(f"  - {md_path}")
    print(f"  - {excel_path}")
    print(f"  - {summary_path}")


if __name__ == "__main__":
    main()
