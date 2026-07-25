"""Feature engineering for CloudGuardian ML model"""

import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_exploitability_score(finding: Dict) -> int:
    """
    Calculate exploitability score (0-3)
    0 = Very difficult
    1 = Difficult (requires inside knowledge)
    2 = Moderate (requires some skill)
    3 = Easy (script kiddie level)
    """
    # Public exposure makes exploitation easier
    if finding.get('public_exposure', 0) == 1:
        base_score = 3
    else:
        base_score = 1
    
    # Certain misconfigurations are easier to exploit
    easy_exploits = ['open', 'public', '0.0.0.0/0', 'wildcard', 'admin']
    risk_text = finding.get('risk', '').lower()
    
    if any(keyword in risk_text for keyword in easy_exploits):
        return min(base_score + 1, 3)
    
    return base_score

def calculate_blast_radius(finding: Dict) -> int:
    """
    Calculate blast radius / impact scope (0-3)
    0 = Single resource
    1 = Multiple resources, same service
    2 = Multiple services
    3 = Account-wide / Cross-account
    """
    service = finding.get('service', '').lower()
    resource = finding.get('resource', '').lower()
    
    # IAM and account-level issues have highest blast radius
    account_level = ['iam', 'cloudtrail', 'config', 'guardduty']
    if service in account_level:
        return 3
    
    # Data services have medium-high blast radius
    data_services = ['s3', 'rds', 'dynamodb', 'redshift']
    if service in data_services:
        return 2
    
    # Compute services have medium blast radius
    compute_services = ['ec2', 'lambda', 'ecs', 'eks']
    if service in compute_services:
        return 1
    
    return 1

def count_compliance_frameworks(finding: Dict) -> int:
    """Count number of compliance frameworks violated"""
    compliance_data = finding.get('compliance', {})
    if isinstance(compliance_data, dict):
        return len(compliance_data)
    return 0

def extract_resource_count(finding: Dict) -> int:
    """Extract number of affected resources"""
    # For now, assume 1 resource per finding
    # In production, this would aggregate across similar findings
    return 1

def engineer_features(findings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features for ML model
    
    Args:
        findings_df: DataFrame with consolidated findings
    
    Returns:
        DataFrame with engineered features
    """
    df = findings_df.copy()
    
    # Convert to dict for feature calculation
    findings_list = df.to_dict('records')
    
    # Calculate additional features
    exploitability_scores = [calculate_exploitability_score(f) for f in findings_list]
    blast_radius_scores = [calculate_blast_radius(f) for f in findings_list]
    compliance_counts = [count_compliance_frameworks(f) for f in findings_list]
    resource_counts = [extract_resource_count(f) for f in findings_list]
    
    # Add to dataframe
    df['exploitability'] = exploitability_scores
    df['blast_radius'] = blast_radius_scores
    df['compliance_frameworks'] = compliance_counts
    df['resource_count'] = resource_counts
    
    # Ensure required features exist
    if 'severity_score' not in df.columns:
        severity_map = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}
        df['severity_score'] = df['severity'].map(severity_map)
    
    if 'service_critical' not in df.columns:
        critical_services = ['iam', 's3', 'rds', 'ec2', 'cloudtrail']
        df['service_critical'] = df['service'].str.lower().isin(critical_services).astype(int)
    
    if 'public_exposure' not in df.columns:
        df['public_exposure'] = 0
    
    if 'encryption_issue' not in df.columns:
        df['encryption_issue'] = 0
    
    return df

def create_target_labels(findings_df: pd.DataFrame) -> pd.Series:
    """
    Create target labels for supervised learning
    Uses rule-based heuristics to generate labels
    
    Priority Logic:
    - CRITICAL: severity=CRITICAL + (public_exposure OR service_critical)
    - HIGH: severity=HIGH OR (severity=CRITICAL + low blast radius)
    - MEDIUM: severity=MEDIUM OR (severity=HIGH + low exploitability)
    - LOW: Everything else
    """
    labels = []
    
    for _, row in findings_df.iterrows():
        severity = row['severity']
        public = row.get('public_exposure', 0)
        critical_svc = row.get('service_critical', 0)
        exploitability = row.get('exploitability', 1)
        blast = row.get('blast_radius', 1)
        
        if severity == 'CRITICAL' and (public == 1 or critical_svc == 1):
            labels.append('CRITICAL')
        elif severity == 'CRITICAL' or (severity == 'HIGH' and blast >= 2):
            labels.append('HIGH')
        elif severity == 'HIGH' or (severity == 'MEDIUM' and exploitability >= 2):
            labels.append('MEDIUM')
        else:
            labels.append('LOW')
    
    return pd.Series(labels, index=findings_df.index)

def get_feature_columns() -> List[str]:
    """Return list of feature column names for model training"""
    return [
        'severity_score',
        'service_critical',
        'public_exposure',
        'encryption_issue',
        'resource_count',
        'compliance_frameworks',
        'exploitability',
        'blast_radius'
    ]
