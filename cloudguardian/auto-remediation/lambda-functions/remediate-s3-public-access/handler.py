"""
AWS Lambda: S3 Public Access Remediation

Automatically remediates publicly accessible S3 buckets by enabling
public access block configuration.

Trigger: EventBridge rule on S3 bucket creation/modification
"""

import json
import boto3
import logging
from typing import Dict
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# Configuration
EXCEPTION_BUCKETS = [
    # Whitelist buckets that should remain public (e.g., static websites)
]

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:782700525901:cloudguardian-alerts'


def pre_remediation_checks(bucket_name: str) -> Dict:
    """Perform pre-remediation safety checks"""
    if bucket_name in EXCEPTION_BUCKETS:
        return {'proceed': False, 'reason': f'Bucket {bucket_name} is in exception list'}
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        return {'proceed': False, 'reason': f'Bucket not found: {str(e)}'}
    
    try:
        s3_client.get_bucket_website(Bucket=bucket_name)
        return {'proceed': False, 'reason': f'Bucket configured for static website hosting'}
    except ClientError as e:
        if e.response['Error']['Code'] != 'NoSuchWebsiteConfiguration':
            logger.warning(f'Error checking website config: {e}')
    
    return {'proceed': True, 'reason': 'All pre-checks passed'}


def remediate_s3_public_access(bucket_name: str) -> Dict:
    """Block public access on S3 bucket"""
    try:
        response = s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        logger.info(f'Successfully blocked public access on {bucket_name}')
        return {'success': True, 'bucket': bucket_name, 'action': 'Public access blocked'}
    
    except ClientError as e:
        logger.error(f'Failed to remediate {bucket_name}: {e}')
        return {'success': False, 'bucket': bucket_name, 'error': str(e)}


def post_remediation_verification(bucket_name: str) -> Dict:
    """Verify remediation was successful"""
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        config = response['PublicAccessBlockConfiguration']
        all_blocked = all([
            config['BlockPublicAcls'],
            config['IgnorePublicAcls'],
            config['BlockPublicPolicy'],
            config['RestrictPublicBuckets']
        ])
        return {'verified': all_blocked, 'configuration': config}
    except ClientError as e:
        return {'verified': False, 'error': str(e)}


def send_notification(bucket_name: str, result: Dict):
    """Send SNS notification about remediation action"""
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'CloudGuardian: S3 Remediation - {bucket_name}',
            Message=json.dumps({'bucket': bucket_name, 'result': result}, indent=2)
        )
    except Exception as e:
        logger.warning(f'Failed to send notification: {e}')


def lambda_handler(event: Dict, context) -> Dict:
    """Main Lambda handler"""
    logger.info(f'Received event: {json.dumps(event)}')
    
    try:
        if 'detail' in event:
            bucket_name = event['detail'].get('requestParameters', {}).get('bucketName')
        elif 'bucket' in event:
            bucket_name = event['bucket']
        else:
            raise ValueError('Cannot extract bucket name from event')
        
        if not bucket_name:
            raise ValueError('Bucket name is empty')
    except (KeyError, ValueError) as e:
        return {'statusCode': 400, 'error': f'Invalid event: {str(e)}'}
    
    pre_check = pre_remediation_checks(bucket_name)
    if not pre_check['proceed']:
        return {'statusCode': 200, 'action': 'skipped', 'reason': pre_check['reason']}
    
    remediation_result = remediate_s3_public_access(bucket_name)
    
    if remediation_result['success']:
        remediation_result['verification'] = post_remediation_verification(bucket_name)
    
    send_notification(bucket_name, remediation_result)
    
    return {
        'statusCode': 200 if remediation_result['success'] else 500,
        'result': remediation_result
    }
