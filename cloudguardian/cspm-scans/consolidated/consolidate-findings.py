#!/usr/bin/env python3
"""
CloudGuardian CSPM Findings Consolidation Script
Consolidates findings from Prowler, Steampipe, and ScoutSuite into a unified format
"""

import json
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, List

# Paths
PROWLER_DIR = Path("../prowler/outputs")
STEAMPIPE_DIR = Path("../steampipe/outputs")
SCOUTSUITE_DIR = Path("../scoutsuite/outputs")
OUTPUT_FILE = Path("./consolidated-findings.json")
CSV_OUTPUT = Path("./consolidated-findings.csv")

def normalize_severity(severity: str) -> str:
    """Normalize severity levels across tools"""
    severity_map = {
        "critical": "CRITICAL",
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
        "informational": "INFO",
        "info": "INFO"
    }
    return severity_map.get(severity.lower(), "MEDIUM")

def generate_finding_id(finding: Dict) -> str:
    """Generate unique finding ID based on resource and check"""
    unique_str = f"{finding['resource']}{finding['check_id']}{finding['service']}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:12]

def parse_prowler_findings(prowler_dir: Path) -> List[Dict]:
    """Parse Prowler JSON output"""
    findings = []
    json_file = prowler_dir / "prowler-output.json"
    
    if not json_file.exists():
        print(f"Warning: Prowler output not found at {json_file}")
        return findings
    
    with open(json_file, 'r') as f:
        prowler_data = json.load(f)
    
    for item in prowler_data:
        if item.get('Status') == 'FAIL':
            finding = {
                'source': 'Prowler',
                'finding_id': generate_finding_id({
                    'resource': item.get('ResourceId', 'unknown'),
                    'check_id': item.get('CheckID', 'unknown'),
                    'service': item.get('ServiceName', 'unknown')
                }),
                'check_id': item.get('CheckID', ''),
                'check_title': item.get('CheckTitle', ''),
                'service': item.get('ServiceName', ''),
                'resource': item.get('ResourceId', ''),
                'resource_type': item.get('ResourceType', ''),
                'region': item.get('Region', 'us-east-1'),
                'status': 'FAIL',
                'severity': normalize_severity(item.get('Severity', 'medium')),
                'risk': item.get('Risk', ''),
                'remediation': item.get('Remediation', ''),
                'compliance': item.get('Compliance', {}),
                'timestamp': datetime.now().isoformat()
            }
            findings.append(finding)
    
    print(f"Parsed {len(findings)} failed checks from Prowler")
    return findings

def parse_steampipe_findings(steampipe_dir: Path) -> List[Dict]:
    """Parse Steampipe CSV output"""
    findings = []
    csv_file = steampipe_dir / "steampipe-findings.csv"
    
    if not csv_file.exists():
        print(f"Warning: Steampipe output not found at {csv_file}")
        return findings
    
    df = pd.read_csv(csv_file)
    
    for _, row in df.iterrows():
        if row.get('status', '').lower() == 'alarm':
            finding = {
                'source': 'Steampipe',
                'finding_id': generate_finding_id({
                    'resource': str(row.get('resource', 'unknown')),
                    'check_id': str(row.get('control', 'unknown')),
                    'service': 'aws'
                }),
                'check_id': str(row.get('control', '')),
                'check_title': str(row.get('title', '')),
                'service': 'aws',
                'resource': str(row.get('resource', '')),
                'resource_type': str(row.get('type', '')),
                'region': 'us-east-1',
                'status': 'FAIL',
                'severity': normalize_severity(str(row.get('severity', 'medium'))),
                'risk': str(row.get('reason', '')),
                'remediation': '',
                'compliance': {},
                'timestamp': datetime.now().isoformat()
            }
            findings.append(finding)
    
    print(f"Parsed {len(findings)} failed checks from Steampipe")
    return findings

def deduplicate_findings(findings: List[Dict]) -> List[Dict]:
    """Remove duplicate findings across tools"""
    unique_findings = {}
    
    for finding in findings:
        key = (finding['resource'], finding['check_id'])
        
        if key not in unique_findings:
            unique_findings[key] = finding
        else:
            # Keep finding with more details
            if len(finding['remediation']) > len(unique_findings[key]['remediation']):
                unique_findings[key] = finding
    
    return list(unique_findings.values())

def enrich_findings(findings: List[Dict]) -> List[Dict]:
    """Add ML-ready features to findings"""
    for finding in findings:
        # Severity score
        severity_scores = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1,
            'INFO': 0
        }
        finding['severity_score'] = severity_scores.get(finding['severity'], 2)
        
        # Service criticality (example heuristics)
        critical_services = ['iam', 's3', 'rds', 'ec2']
        finding['service_critical'] = 1 if finding['service'].lower() in critical_services else 0
        
        # Public exposure indicators
        public_indicators = ['public', '0.0.0.0/0', 'internet', 'open']
        finding['public_exposure'] = 1 if any(ind in finding['risk'].lower() for ind in public_indicators) else 0
        
        # Encryption indicators
        encryption_indicators = ['encrypt', 'kms', 'ssl', 'tls']
        finding['encryption_issue'] = 1 if any(ind in finding['check_title'].lower() for ind in encryption_indicators) else 0
    
    return findings

def main():
    print("="*50)
    print("CloudGuardian CSPM Findings Consolidation")
    print("="*50)
    print()
    
    # Parse findings from all sources
    all_findings = []
    all_findings.extend(parse_prowler_findings(PROWLER_DIR))
    all_findings.extend(parse_steampipe_findings(STEAMPIPE_DIR))
    
    print(f"\nTotal findings before deduplication: {len(all_findings)}")
    
    # Deduplicate
    unique_findings = deduplicate_findings(all_findings)
    print(f"Unique findings after deduplication: {len(unique_findings)}")
    
    # Enrich with ML features
    enriched_findings = enrich_findings(unique_findings)
    
    # Save JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(enriched_findings, f, indent=2)
    print(f"\n✓ Saved consolidated findings to {OUTPUT_FILE}")
    
    # Save CSV
    if enriched_findings:
        df = pd.DataFrame(enriched_findings)
        df.to_csv(CSV_OUTPUT, index=False)
        print(f"✓ Saved CSV output to {CSV_OUTPUT}")
        
        # Print summary statistics
        print("\n" + "="*50)
        print("Summary Statistics")
        print("="*50)
        print(f"Total unique findings: {len(enriched_findings)}")
        print(f"\nBy Severity:")
        print(df['severity'].value_counts())
        print(f"\nBy Service:")
        print(df['service'].value_counts().head(10))
        print(f"\nBy Source:")
        print(df['source'].value_counts())
    
    print("\n✓ Consolidation complete!")
    print("\nNext steps:")
    print("  1. Run ML prioritization: cd ../../ml-prioritization && jupyter notebook")
    print("  2. Review findings: cat consolidated-findings.json")
    print()

if __name__ == "__main__":
    main()
