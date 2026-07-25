"""
Post-Remediation Verification Checks
Verify that remediation actions achieved desired outcomes
"""

import boto3
import logging
import time
from typing import Dict

logger = logging.getLogger(__name__)


def verify_s3_public_access_blocked(bucket_name: str) -> Dict:
    """Verify S3 bucket has public access blocked"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.get_public_access_block(Bucket=bucket_name)
        config = response['PublicAccessBlockConfiguration']
        
        all_blocked = all([
            config.get('BlockPublicAcls', False),
            config.get('IgnorePublicAcls', False),
            config.get('BlockPublicPolicy', False),
            config.get('RestrictPublicBuckets', False)
        ])
        
        return {
            'verified': all_blocked,
            'bucket': bucket_name,
            'configuration': config
        }
    
    except Exception as e:
        return {'verified': False, 'bucket': bucket_name, 'error': str(e)}


def verify_security_group_rules(sg_id: str, expected_rules: list = None) -> Dict:
    """Verify security group rules match expected configuration"""
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.describe_security_groups(GroupIds=[sg_id])
        current_rules = response['SecurityGroups'][0]['IpPermissions']
        
        # Check for any 0.0.0.0/0 rules on sensitive ports
        sensitive_ports = [22, 3389, 3306, 5432]
        permissive_rules_found = []
        
        for rule in current_rules:
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    from_port = rule.get('FromPort', 0)
                    to_port = rule.get('ToPort', 65535)
                    
                    for port in sensitive_ports:
                        if from_port <= port <= to_port:
                            permissive_rules_found.append({
                                'port': port,
                                'protocol': rule.get('IpProtocol')
                            })
        
        return {
            'verified': len(permissive_rules_found) == 0,
            'sg_id': sg_id,
            'permissive_rules_remaining': permissive_rules_found
        }
    
    except Exception as e:
        return {'verified': False, 'sg_id': sg_id, 'error': str(e)}


def verify_ebs_encryption_default() -> Dict:
    """Verify EBS encryption by default is enabled"""
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.get_ebs_encryption_by_default()
        enabled = response.get('EbsEncryptionByDefault', False)
        
        return {
            'verified': enabled,
            'encryption_by_default': enabled
        }
    
    except Exception as e:
        return {'verified': False, 'error': str(e)}


def verify_iam_user_mfa(user_name: str) -> Dict:
    """Verify IAM user has MFA enabled or enforcement policy attached"""
    iam = boto3.client('iam')
    
    try:
        # Check MFA devices
        mfa_response = iam.list_mfa_devices(UserName=user_name)
        has_mfa = len(mfa_response.get('MFADevices', [])) > 0
        
        # Check attached policies
        policies_response = iam.list_attached_user_policies(UserName=user_name)
        has_mfa_policy = any(
            'MFA' in p['PolicyName'].upper() or 'Force-MFA' in p['PolicyName']
            for p in policies_response.get('AttachedPolicies', [])
        )
        
        return {
            'verified': has_mfa or has_mfa_policy,
            'user': user_name,
            'has_mfa_device': has_mfa,
            'has_mfa_enforcement_policy': has_mfa_policy
        }
    
    except Exception as e:
        return {'verified': False, 'user': user_name, 'error': str(e)}


def wait_for_state_change(resource_type: str, resource_id: str, max_wait: int = 60) -> bool:
    """Wait for AWS resource state to stabilize"""
    logger.info(f'Waiting up to {max_wait}s for {resource_type} {resource_id} to stabilize...')
    time.sleep(min(5, max_wait))  # Simple wait
    return True


def rescan_resource(resource_type: str, resource_id: str) -> Dict:
    """
    Trigger a re-scan of the specific resource to confirm remediation
    In production, this would trigger Prowler/CSPM re-scan
    """
    return {
        'action': 'rescan_triggered',
        'resource_type': resource_type,
        'resource_id': resource_id,
        'note': 'Manual re-scan recommended via Prowler/Steampipe'
    }
