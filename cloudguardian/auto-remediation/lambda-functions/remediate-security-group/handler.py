"""
AWS Lambda: Security Group Hardening

Automatically removes overly permissive security group rules (0.0.0.0/0)
on sensitive ports.
"""

import json
import boto3
import logging
from typing import Dict, List
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')
sns_client = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:782700525901:cloudguardian-alerts'

# Sensitive ports that should NEVER be open to 0.0.0.0/0
SENSITIVE_PORTS = {
    22: 'SSH',
    23: 'Telnet',
    3389: 'RDP',
    3306: 'MySQL',
    5432: 'PostgreSQL',
    27017: 'MongoDB',
    6379: 'Redis',
    9200: 'Elasticsearch',
    5984: 'CouchDB',
    9042: 'Cassandra',
    11211: 'Memcached',
    1433: 'MSSQL',
    1521: 'Oracle',
    5000: 'Docker Registry',
    8080: 'HTTP Alt (often internal)',
}

# Ports that can be public (approved public-facing services)
APPROVED_PUBLIC_PORTS = {80, 443, 53}


def get_security_group_rules(sg_id: str) -> List[Dict]:
    """Get all ingress rules for a security group"""
    try:
        response = ec2_client.describe_security_groups(GroupIds=[sg_id])
        return response['SecurityGroups'][0]['IpPermissions']
    except ClientError as e:
        logger.error(f'Failed to get SG rules: {e}')
        return []


def find_permissive_rules(sg_id: str) -> List[Dict]:
    """Find rules that expose sensitive ports to 0.0.0.0/0"""
    permissive_rules = []
    rules = get_security_group_rules(sg_id)
    
    for rule in rules:
        # Check for 0.0.0.0/0 CIDR
        for ip_range in rule.get('IpRanges', []):
            if ip_range.get('CidrIp') == '0.0.0.0/0':
                from_port = rule.get('FromPort', 0)
                to_port = rule.get('ToPort', 65535)
                protocol = rule.get('IpProtocol', '')
                
                # Check if any sensitive ports are in range
                for port in SENSITIVE_PORTS:
                    if from_port <= port <= to_port and port not in APPROVED_PUBLIC_PORTS:
                        permissive_rules.append({
                            'protocol': protocol,
                            'from_port': from_port,
                            'to_port': to_port,
                            'cidr': '0.0.0.0/0',
                            'sensitive_port': port,
                            'service': SENSITIVE_PORTS[port]
                        })
                        break
    
    return permissive_rules


def revoke_permissive_rule(sg_id: str, rule: Dict) -> Dict:
    """Revoke a permissive security group rule"""
    try:
        ec2_client.revoke_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[{
                'IpProtocol': rule['protocol'],
                'FromPort': rule['from_port'],
                'ToPort': rule['to_port'],
                'IpRanges': [{'CidrIp': rule['cidr']}]
            }]
        )
        
        logger.info(f'Revoked permissive rule for {rule[\"service\"]} on SG {sg_id}')
        return {
            'success': True,
            'sg_id': sg_id,
            'rule_revoked': rule,
            'action': f'Removed public access to {rule[\"service\"]}'
        }
    
    except ClientError as e:
        logger.error(f'Failed to revoke rule: {e}')
        return {'success': False, 'sg_id': sg_id, 'error': str(e)}


def backup_security_group(sg_id: str) -> Dict:
    """Backup security group configuration before modification"""
    try:
        response = ec2_client.describe_security_groups(GroupIds=[sg_id])
        sg_config = response['SecurityGroups'][0]
        
        # Store backup in a systems manager parameter for rollback
        ssm_client = boto3.client('ssm')
        param_name = f'/cloudguardian/backup/sg-{sg_id}'
        
        ssm_client.put_parameter(
            Name=param_name,
            Value=json.dumps(sg_config, default=str),
            Type='String',
            Overwrite=True,
            Description=f'CloudGuardian backup of {sg_id}'
        )
        
        return {'backed_up': True, 'backup_location': param_name}
    
    except ClientError as e:
        logger.warning(f'Backup failed for {sg_id}: {e}')
        return {'backed_up': False, 'error': str(e)}


def lambda_handler(event: Dict, context) -> Dict:
    """Main Lambda handler"""
    logger.info(f'Received event: {json.dumps(event)}')
    
    try:
        if 'sg_id' in event:
            sg_id = event['sg_id']
        elif 'detail' in event:
            sg_id = event['detail'].get('requestParameters', {}).get('groupId')
        else:
            raise ValueError('Cannot extract SG ID from event')
        
        if not sg_id:
            raise ValueError('Security Group ID is empty')
    except (KeyError, ValueError) as e:
        return {'statusCode': 400, 'error': f'Invalid event: {str(e)}'}
    
    logger.info(f'Processing security group: {sg_id}')
    
    # Find permissive rules
    permissive_rules = find_permissive_rules(sg_id)
    
    if not permissive_rules:
        return {
            'statusCode': 200,
            'action': 'no_action_needed',
            'sg_id': sg_id,
            'message': 'No permissive rules found'
        }
    
    # Backup before modification
    backup_result = backup_security_group(sg_id)
    
    # Revoke each permissive rule
    revocation_results = []
    for rule in permissive_rules:
        result = revoke_permissive_rule(sg_id, rule)
        revocation_results.append(result)
    
    # Summary
    successful_revocations = sum(1 for r in revocation_results if r['success'])
    
    summary = {
        'sg_id': sg_id,
        'permissive_rules_found': len(permissive_rules),
        'rules_revoked': successful_revocations,
        'rules_failed': len(permissive_rules) - successful_revocations,
        'backup': backup_result,
        'details': revocation_results
    }
    
    # Send notification
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f'CloudGuardian: Security Group Hardening - {sg_id}',
            Message=json.dumps(summary, indent=2, default=str)
        )
    except Exception as e:
        logger.warning(f'Notification failed: {e}')
    
    return {
        'statusCode': 200 if successful_revocations > 0 else 500,
        'result': summary
    }
