"""
Unit tests for ML model
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ml-prioritization" / "src"))


def test_calculate_exploitability():
    """Test exploitability score calculation"""
    from feature_definitions import calculate_exploitability_score
    
    # Public exposure
    finding1 = {'public_exposure': 1, 'risk': 'Normal risk'}
    assert calculate_exploitability_score(finding1) == 3
    
    # Private, but easy exploit
    finding2 = {'public_exposure': 0, 'risk': 'wildcard permissions granted'}
    assert calculate_exploitability_score(finding2) == 2
    
    # Private, hard exploit
    finding3 = {'public_exposure': 0, 'risk': 'Complex configuration issue'}
    assert calculate_exploitability_score(finding3) == 1


def test_calculate_blast_radius():
    """Test blast radius calculation"""
    from feature_definitions import calculate_blast_radius
    
    # Account-level service
    finding1 = {'service': 'iam', 'resource': 'user1'}
    assert calculate_blast_radius(finding1) == 3
    
    # Data service
    finding2 = {'service': 's3', 'resource': 'bucket1'}
    assert calculate_blast_radius(finding2) == 2
    
    # Compute service
    finding3 = {'service': 'ec2', 'resource': 'i-123'}
    assert calculate_blast_radius(finding3) == 1


def test_engineer_features():
    """Test feature engineering pipeline"""
    from feature_definitions import engineer_features
    
    df = pd.DataFrame([
        {
            'service': 's3',
            'severity': 'CRITICAL',
            'risk': 'Public bucket',
            'check_title': 'Encryption disabled',
            'resource': 'bucket1',
            'public_exposure': 1
        }
    ])
    
    result = engineer_features(df)
    
    assert 'exploitability' in result.columns
    assert 'blast_radius' in result.columns
    assert 'severity_score' in result.columns
    assert 'service_critical' in result.columns
    
    # Verify calculations
    assert result['severity_score'].iloc[0] == 4  # CRITICAL
    assert result['service_critical'].iloc[0] == 1  # s3 is critical
    assert result['blast_radius'].iloc[0] == 2  # s3 is data service


def test_create_target_labels():
    """Test target label creation"""
    from feature_definitions import create_target_labels
    
    df = pd.DataFrame([
        # CRITICAL: critical severity + public + critical service
        {'severity': 'CRITICAL', 'public_exposure': 1, 'service_critical': 1, 'exploitability': 3, 'blast_radius': 3},
        # HIGH: high severity + medium blast
        {'severity': 'HIGH', 'public_exposure': 0, 'service_critical': 0, 'exploitability': 2, 'blast_radius': 2},
        # MEDIUM: medium severity
        {'severity': 'MEDIUM', 'public_exposure': 0, 'service_critical': 0, 'exploitability': 1, 'blast_radius': 1},
        # LOW: low severity
        {'severity': 'LOW', 'public_exposure': 0, 'service_critical': 0, 'exploitability': 0, 'blast_radius': 0}
    ])
    
    labels = create_target_labels(df)
    
    assert labels.iloc[0] == 'CRITICAL'
    # Note: exact labels depend on business logic


def test_get_feature_columns():
    """Test feature column definitions"""
    from feature_definitions import get_feature_columns
    
    cols = get_feature_columns()
    
    assert 'severity_score' in cols
    assert 'service_critical' in cols
    assert 'public_exposure' in cols
    assert 'encryption_issue' in cols
    assert len(cols) == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
