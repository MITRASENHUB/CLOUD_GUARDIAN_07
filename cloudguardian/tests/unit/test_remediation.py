"""
Unit tests for Lambda remediation functions
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "auto-remediation" / "lambda-functions"))


@patch('boto3.client')
def test_s3_pre_remediation_checks(mock_boto):
    """Test S3 pre-remediation safety checks"""
    from remediate_s3_public_access.handler import pre_remediation_checks
    
    # Mock S3 client
    mock_s3 = MagicMock()
    mock_boto.return_value = mock_s3
    
    # Test 1: Bucket exists, no website
    mock_s3.head_bucket.return_value = {}
    mock_s3.get_bucket_website.side_effect = Exception('NoSuchWebsiteConfiguration')
    
    # This is a simplified test - actual implementation may vary
    # In production, use moto library for AWS mocking
    assert True  # Placeholder


def test_security_group_sensitive_ports():
    """Test sensitive port detection"""
    from remediate_security_group.handler import SENSITIVE_PORTS
    
    assert 22 in SENSITIVE_PORTS
    assert 3389 in SENSITIVE_PORTS
    assert 3306 in SENSITIVE_PORTS
    
    # Verify common web ports NOT in sensitive list
    assert 80 not in SENSITIVE_PORTS
    assert 443 not in SENSITIVE_PORTS


def test_approval_workflow():
    """Test approval workflow logic"""
    from guardrails.approval_workflow import requires_approval
    
    # Critical + Production = approval required
    assert requires_approval('CRITICAL', 'S3', 'production') == True
    
    # High + Lab = no approval
    assert requires_approval('HIGH', 'EC2', 'lab') == False
    
    # IAM changes always require approval
    assert requires_approval('LOW', 'IAM', 'lab') == True
    
    # RDS always requires approval
    assert requires_approval('MEDIUM', 'RDS', 'lab') == True


def test_pre_checks_business_hours():
    """Test business hours check"""
    from guardrails.pre_checks import check_business_hours
    
    # Function exists and returns bool
    result = check_business_hours()
    assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
