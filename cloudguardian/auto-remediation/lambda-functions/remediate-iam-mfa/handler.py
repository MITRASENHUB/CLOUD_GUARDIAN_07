"""
AWS Lambda: IAM MFA Enforcement Remediation

Automatically enforces MFA for IAM users with console access.
"""

import json
import boto3
import logging
from typing import Dict, List
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

iam_client = boto3.client('iam')
sns_client = boto3.client('sns')

BREAK_GLASS_USERS = ['emergency-admin']
GRACE_PERIOD_DAYS = 7
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:782700525901:cloudguardian-alerts'

MFA_ENFORCEMENT_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowViewAccountInfo",
            "Effect": "Allow",
            "Action": [
                "iam:GetAccountPasswordPolicy",
                "iam:ListMFADevices",
                "iam:ListUsers"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DenyAllExceptListedIfNoMFA",
            "Effect": "Deny",
            "NotAction": [
                "iam:CreateVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListVirtualMFADevices",
                "iam:ResyncMFADevice",
                "sts:GetSessionToken"
            ],
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": "false"
                }
            }
        }
    ]
}


def is_user_in_grace_period(user_name: str) -> bool:
    """Check if user is within grace period (new user)"""
    try:
        response = iam_client.get_user(UserName=user_name)
        from datetime import datetime, timezone, timedelta
        create_date = response['User']['CreateDate']
        age = datetime.now(timezone.utc) - create_date
        return age < timedelta(days=GRACE_PERIOD_DAYS)
    except ClientError:
        return False


def has_mfa_enabled(user_name: str) -> bool:
    """Check if user has MFA enabled"""
    try:
        response = iam_client.list_mfa_devices(UserName=user_name)
        return len(response.get('MFADevices', [])) > 0
    except ClientError as e:
        logger.error(f'Failed to check MFA for {user_name}: {e}')
        return False


def has_console_access(user_name: str) -> bool:
    """Check if user has console (login profile) access"""
    try:
        iam_client.get_login_profile(UserName=user_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            return False
        raise


def enforce_mfa_policy(user_name: str) -> Dict:
    """Attach MFA enforcement policy to user"""
    try:
        # Create policy if not exists
        policy_name = 'CloudGuardian-Force-MFA'
        account_id = boto3.client('sts').get_caller_identity()['Account']
        policy_arn = f'arn:aws:iam::{account_id}:policy/{policy_name}'
        
        try:
            iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(MFA_ENFORCEMENT_POLICY),
                Description='CloudGuardian - Force MFA for console access'
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'EntityAlreadyExists':
                raise
        
        # Attach policy to user
        iam_client.attach_user_policy(
            UserName=user_name,
            PolicyArn=policy_arn
        )
        
        logger.info(f'MFA enforcement policy attached to {user_name}')
        return {'success': True, 'user': user_name, 'policy': policy_arn}
    
    except ClientError as e:
        logger.error(f'Failed to enforce MFA for {user_name}: {e}')
        return {'success': False, 'user': user_name, 'error': str(e)}


def lambda_handler(event: Dict, context) -> Dict:
    """Main Lambda handler"""
    logger.info(f'Received event: {json.dumps(event)}')
    
    try:
        # Get user name from event
        if 'user_name' in event:
            user_name = event['user_name']
        elif 'detail' in event:
            user_name = event['detail'].get('userIdentity', {}).get('userName')
        else:
            raise ValueError('Cannot extract user name from event')
        
        if not user_name:
            raise ValueError('User name is empty')
    except (KeyError, ValueError) as e:
        return {'statusCode': 400, 'error': f'Invalid event: {str(e)}'}
    
    # Pre-checks
    if user_name in BREAK_GLASS_USERS:
        return {'statusCode': 200, 'action': 'skipped', 'reason': 'Break-glass account excluded'}
    
    if not has_console_access(user_name):
        return {'statusCode': 200, 'action': 'skipped', 'reason': 'No console access'}
    
    if has_mfa_enabled(user_name):
        return {'statusCode': 200, 'action': 'skipped', 'reason': 'MFA already enabled'}
    
    if is_user_in_grace_period(user_name):
        return {'statusCode': 200, 'action': 'skipped', 'reason': 'User in grace period'}
    
    # Enforce MFA
    result = enforce_mfa_policy(user_name)
    
    # Send notification
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'CloudGuardian: MFA Enforcement - {user_name}',
            Message=json.dumps(result, indent=2)
        )
    except Exception as e:
        logger.warning(f'Notification failed: {e}')
    
    return {'statusCode': 200 if result['success'] else 500, 'result': result}
