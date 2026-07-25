"""
Pre-Remediation Safety Checks
Common validation logic used across all Lambda functions
"""

import boto3
import logging
from typing import Dict
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


def check_business_hours(timezone_offset: int = 0) -> bool:
    """
    Check if current time is within business hours (9 AM - 6 PM UTC)
    
    Args:
        timezone_offset: Hours to add/subtract from UTC
    
    Returns:
        True if within business hours
    """
    now = datetime.now(timezone.utc) + timedelta(hours=timezone_offset)
    hour = now.hour
    return 9 <= hour < 18


def check_resource_tags(resource_arn: str, required_tags: Dict) -> bool:
    """
    Check if resource has required tags
    
    Args:
        resource_arn: AWS resource ARN
        required_tags: Dict of tag key-value pairs
    
    Returns:
        True if all required tags are present
    """
    try:
        client = boto3.client('resourcegroupstaggingapi')
        response = client.get_resources(ResourceARNList=[resource_arn])
        
        if not response.get('ResourceTagMappingList'):
            return False
        
        resource_tags = {
            tag['Key']: tag['Value']
            for tag in response['ResourceTagMappingList'][0].get('Tags', [])
        }
        
        for key, value in required_tags.items():
            if resource_tags.get(key) != value:
                return False
        
        return True
    
    except Exception as e:
        logger.error(f'Failed to check tags: {e}')
        return False


def check_production_environment(resource_arn: str) -> bool:
    """Check if resource is in production environment"""
    return check_resource_tags(resource_arn, {'Environment': 'production'})


def check_approval_required(severity: str, resource_type: str) -> bool:
    """
    Determine if manual approval is required
    
    Args:
        severity: Finding severity
        resource_type: Type of resource
    
    Returns:
        True if approval is required
    """
    # Always require approval for critical findings on production resources
    if severity == 'CRITICAL':
        return True
    
    # Always require approval for high-impact resource types
    high_impact_types = ['RDS', 'CloudTrail', 'KMS', 'IAM']
    if resource_type in high_impact_types:
        return True
    
    return False


def get_active_connections(resource_id: str, service: str) -> int:
    """
    Get number of active connections/usage for a resource
    Used to prevent disruption of active services
    """
    try:
        cloudwatch = boto3.client('cloudwatch')
        
        # Example: Get RDS active connections
        if service.lower() == 'rds':
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='DatabaseConnections',
                Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': resource_id}],
                StartTime=datetime.now(timezone.utc) - timedelta(minutes=5),
                EndTime=datetime.now(timezone.utc),
                Period=300,
                Statistics=['Average']
            )
            
            if response.get('Datapoints'):
                return int(response['Datapoints'][0]['Average'])
        
        return 0
    
    except Exception as e:
        logger.error(f'Failed to get metrics: {e}')
        return 0


def validate_iam_permissions(action: str) -> bool:
    """Verify Lambda has required IAM permissions for action"""
    try:
        iam = boto3.client('iam')
        sts = boto3.client('sts')
        
        caller_identity = sts.get_caller_identity()
        role_arn = caller_identity['Arn']
        
        # Simulate policy to check permissions
        response = iam.simulate_principal_policy(
            PolicySourceArn=role_arn,
            ActionNames=[action]
        )
        
        return response['EvaluationResults'][0]['EvalDecision'] == 'allowed'
    
    except Exception as e:
        logger.error(f'Failed to validate permissions: {e}')
        return False
