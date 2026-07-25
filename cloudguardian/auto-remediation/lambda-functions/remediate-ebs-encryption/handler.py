"""
AWS Lambda: EBS Encryption Enablement

Enables EBS encryption by default for the account/region.
Note: Cannot encrypt existing volumes without snapshot process.
"""

import json
import boto3
import logging
from typing import Dict
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:782700525901:cloudguardian-alerts'


def check_encryption_by_default() -> bool:
    """Check if EBS encryption by default is enabled"""
    try:
        response = ec2_client.get_ebs_encryption_by_default()
        return response.get('EbsEncryptionByDefault', False)
    except ClientError as e:
        logger.error(f'Failed to check encryption status: {e}')
        return False


def enable_encryption_by_default() -> Dict:
    """Enable EBS encryption by default"""
    try:
        response = ec2_client.enable_ebs_encryption_by_default()
        logger.info('EBS encryption by default enabled')
        return {
            'success': True,
            'action': 'EBS encryption enabled by default',
            'response': response
        }
    except ClientError as e:
        logger.error(f'Failed to enable encryption: {e}')
        return {'success': False, 'error': str(e)}


def get_unencrypted_volumes() -> list:
    """List all unencrypted EBS volumes"""
    unencrypted = []
    try:
        paginator = ec2_client.get_paginator('describe_volumes')
        for page in paginator.paginate(Filters=[{'Name': 'encrypted', 'Values': ['false']}]):
            for volume in page['Volumes']:
                unencrypted.append({
                    'volume_id': volume['VolumeId'],
                    'size': volume['Size'],
                    'state': volume['State'],
                    'attached_instances': [a['InstanceId'] for a in volume.get('Attachments', [])]
                })
    except ClientError as e:
        logger.error(f'Failed to list volumes: {e}')
    
    return unencrypted


def snapshot_and_replace_volume(volume_id: str) -> Dict:
    """
    Create encrypted copy of unencrypted volume
    NOTE: This requires downtime for the attached instance
    """
    try:
        # Get volume details
        volume_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
        volume = volume_response['Volumes'][0]
        
        # Create snapshot
        snapshot_response = ec2_client.create_snapshot(
            VolumeId=volume_id,
            Description=f'CloudGuardian: Pre-encryption snapshot of {volume_id}'
        )
        snapshot_id = snapshot_response['SnapshotId']
        
        logger.info(f'Created snapshot {snapshot_id} for volume {volume_id}')
        
        return {
            'success': True,
            'volume_id': volume_id,
            'snapshot_id': snapshot_id,
            'action': 'Snapshot created - manual replacement required',
            'next_steps': [
                f'Wait for snapshot {snapshot_id} to complete',
                'Copy snapshot with encryption enabled',
                'Create new encrypted volume from encrypted snapshot',
                'Stop instance, detach old volume, attach new encrypted volume',
                'Start instance'
            ]
        }
    
    except ClientError as e:
        return {'success': False, 'volume_id': volume_id, 'error': str(e)}


def lambda_handler(event: Dict, context) -> Dict:
    """Main Lambda handler"""
    logger.info(f'Received event: {json.dumps(event)}')
    
    action = event.get('action', 'enable_default')
    
    results = {
        'timestamp': str(context.aws_request_id) if context else 'test',
        'actions_taken': []
    }
    
    # Action 1: Check current status
    is_encrypted = check_encryption_by_default()
    results['encryption_by_default'] = is_encrypted
    
    # Action 2: Enable if not already enabled
    if not is_encrypted:
        enable_result = enable_encryption_by_default()
        results['actions_taken'].append(enable_result)
    else:
        results['actions_taken'].append({
            'success': True,
            'action': 'EBS encryption already enabled by default'
        })
    
    # Action 3: List unencrypted volumes (informational)
    unencrypted_volumes = get_unencrypted_volumes()
    results['unencrypted_volumes'] = unencrypted_volumes
    results['unencrypted_count'] = len(unencrypted_volumes)
    
    # Optional: Snapshot unencrypted volumes if requested
    if action == 'snapshot_all' and unencrypted_volumes:
        snapshot_results = []
        for vol in unencrypted_volumes[:5]:  # Limit to 5 to avoid throttling
            snapshot_results.append(snapshot_and_replace_volume(vol['volume_id']))
        results['snapshots'] = snapshot_results
    
    # Send notification
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='CloudGuardian: EBS Encryption Remediation',
            Message=json.dumps(results, indent=2, default=str)
        )
    except Exception as e:
        logger.warning(f'Notification failed: {e}')
    
    return {'statusCode': 200, 'result': results}
