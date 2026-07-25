"""
Unit tests for CSPM findings consolidation logic
"""

import pytest
import json
from pathlib import Path
import sys

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cspm-scans" / "consolidated"))


def test_normalize_severity():
    """Test severity normalization"""
    from consolidate_findings import normalize_severity
    
    assert normalize_severity("critical") == "CRITICAL"
    assert normalize_severity("HIGH") == "HIGH"
    assert normalize_severity("Medium") == "MEDIUM"
    assert normalize_severity("info") == "INFO"
    assert normalize_severity("unknown") == "MEDIUM"  # Default


def test_generate_finding_id():
    """Test finding ID generation"""
    from consolidate_findings import generate_finding_id
    
    finding = {
        'resource': 'test-bucket',
        'check_id': 's3_public_access',
        'service': 's3'
    }
    
    id1 = generate_finding_id(finding)
    id2 = generate_finding_id(finding)
    
    # Same input should generate same ID
    assert id1 == id2
    assert len(id1) == 12  # MD5 truncated to 12 chars


def test_enrich_findings():
    """Test findings enrichment with ML features"""
    from consolidate_findings import enrich_findings
    
    findings = [{
        'source': 'Prowler',
        'severity': 'CRITICAL',
        'service': 's3',
        'risk': 'Public S3 bucket exposing sensitive data',
        'check_title': 'S3 bucket encryption disabled',
        'resource': 'test-bucket',
        'check_id': 's3_encryption'
    }]
    
    enriched = enrich_findings(findings)
    
    assert enriched[0]['severity_score'] == 4  # CRITICAL
    assert enriched[0]['service_critical'] == 1  # s3 is critical
    assert enriched[0]['public_exposure'] == 1  # 'public' in risk
    assert enriched[0]['encryption_issue'] == 1  # 'encrypt' in title


def test_deduplicate_findings():
    """Test deduplication logic"""
    from consolidate_findings import deduplicate_findings
    
    findings = [
        {
            'source': 'Prowler',
            'resource': 'bucket-1',
            'check_id': 's3_public',
            'remediation': 'Short'
        },
        {
            'source': 'Steampipe',
            'resource': 'bucket-1',
            'check_id': 's3_public',
            'remediation': 'Much more detailed remediation guidance'
        },
        {
            'source': 'Prowler',
            'resource': 'bucket-2',
            'check_id': 's3_public',
            'remediation': 'Different resource'
        }
    ]
    
    unique = deduplicate_findings(findings)
    
    assert len(unique) == 2  # bucket-1 deduplicated
    # Should keep the one with more detailed remediation
    bucket1_finding = [f for f in unique if f['resource'] == 'bucket-1'][0]
    assert 'detailed' in bucket1_finding['remediation']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
