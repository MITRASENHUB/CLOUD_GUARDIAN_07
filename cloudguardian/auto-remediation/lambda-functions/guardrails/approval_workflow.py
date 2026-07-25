"""
Human Approval Workflow for Critical Remediations

Implements approval mechanism for high-impact security remediations.
"""

import json
import boto3
import logging
from typing import Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')


class ApprovalWorkflow:
    """Manages approval workflow for critical remediations"""
    
    def __init__(self, approval_table_name: str = 'cloudguardian-approvals'):
        self.table = dynamodb.Table(approval_table_name)
    
    def request_approval(self, remediation_details: Dict) -> str:
        """
        Request approval for a remediation action
        
        Args:
            remediation_details: Details about the proposed remediation
        
        Returns:
            approval_id: Unique ID for tracking approval
        """
        approval_id = f"APR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{remediation_details.get('resource', 'UNK')[:8]}"
        
        # Store approval request
        self.table.put_item(Item={
            'approval_id': approval_id,
            'status': 'PENDING',
            'requested_at': datetime.now(timezone.utc).isoformat(),
            'remediation_details': json.dumps(remediation_details),
            'ttl': int((datetime.now(timezone.utc).timestamp())) + 604800  # 7 days
        })
        
        # Notify approvers
        self._notify_approvers(approval_id, remediation_details)
        
        return approval_id
    
    def check_approval(self, approval_id: str) -> Dict:
        """Check approval status"""
        try:
            response = self.table.get_item(Key={'approval_id': approval_id})
            item = response.get('Item', {})
            
            return {
                'approval_id': approval_id,
                'status': item.get('status', 'NOT_FOUND'),
                'approved_by': item.get('approved_by'),
                'approved_at': item.get('approved_at'),
                'comments': item.get('comments')
            }
        except Exception as e:
            logger.error(f'Failed to check approval: {e}')
            return {'approval_id': approval_id, 'status': 'ERROR', 'error': str(e)}
    
    def approve(self, approval_id: str, approver: str, comments: str = '') -> bool:
        """Mark approval as approved"""
        try:
            self.table.update_item(
                Key={'approval_id': approval_id},
                UpdateExpression='SET #status = :s, approved_by = :ab, approved_at = :aa, comments = :c',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':s': 'APPROVED',
                    ':ab': approver,
                    ':aa': datetime.now(timezone.utc).isoformat(),
                    ':c': comments
                }
            )
            return True
        except Exception as e:
            logger.error(f'Failed to approve: {e}')
            return False
    
    def reject(self, approval_id: str, approver: str, reason: str) -> bool:
        """Mark approval as rejected"""
        try:
            self.table.update_item(
                Key={'approval_id': approval_id},
                UpdateExpression='SET #status = :s, approved_by = :ab, approved_at = :aa, comments = :c',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':s': 'REJECTED',
                    ':ab': approver,
                    ':aa': datetime.now(timezone.utc).isoformat(),
                    ':c': reason
                }
            )
            return True
        except Exception as e:
            logger.error(f'Failed to reject: {e}')
            return False
    
    def _notify_approvers(self, approval_id: str, details: Dict):
        """Send notification to approvers"""
        try:
            topic_arn = 'arn:aws:sns:us-east-1:782700525901:cloudguardian-approvals'
            
            message = f"""
CloudGuardian Approval Request

Approval ID: {approval_id}
Resource: {details.get('resource', 'N/A')}
Action: {details.get('action', 'N/A')}
Severity: {details.get('severity', 'N/A')}

To approve, invoke:
aws lambda invoke --function-name cloudguardian-approve \\
  --payload '{{"approval_id": "{approval_id}", "approver": "your-name", "action": "approve"}}' \\
  response.json

To reject, invoke:
aws lambda invoke --function-name cloudguardian-approve \\
  --payload '{{"approval_id": "{approval_id}", "approver": "your-name", "action": "reject", "reason": "..."}}' \\
  response.json
            """
            
            sns.publish(
                TopicArn=topic_arn,
                Subject=f'CloudGuardian Approval Required: {approval_id}',
                Message=message.strip()
            )
        except Exception as e:
            logger.warning(f'Failed to notify approvers: {e}')


def requires_approval(severity: str, resource_type: str, environment: str = 'lab') -> bool:
    """
    Determine if remediation requires human approval
    
    Rules:
    - Critical severity in production always requires approval
    - IAM changes always require approval
    - Cross-account changes require approval
    """
    if severity == 'CRITICAL' and environment == 'production':
        return True
    
    high_impact_types = ['IAM', 'RDS', 'CloudTrail', 'KMS']
    if resource_type in high_impact_types:
        return True
    
    return False
