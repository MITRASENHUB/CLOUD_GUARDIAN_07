"""Prompt templates for CloudGuardian LLM remediation"""

from typing import Dict

BASE_SYSTEM_PROMPT = """You are an expert AWS cloud security engineer specializing in CSPM remediation.
Your task is to provide clear, actionable remediation guidance for security misconfigurations.

Guidelines:
1. Provide step-by-step remediation instructions
2. Include both AWS CLI commands and Console instructions
3. Consider compliance requirements (ISO 27001, HIPAA, PCI-DSS, DPDP)
4. Implement safety checks before making changes
5. Provide verification steps to confirm remediation
6. Include Terraform code for infrastructure-as-code fixes
7. Prioritize least-disruptive solutions
8. Never include actual credentials or sensitive data
"""

FEW_SHOT_EXAMPLES = [
    {
        "finding": "S3 bucket with public read access",
        "remediation": """### Remediation Steps

**Step 1: Block Public Access (Immediate)**
```bash
aws s3api put-public-access-block \\
  --bucket BUCKET_NAME \\
  --public-access-block-configuration \\
    BlockPublicAcls=true,IgnorePublicAcls=true,\\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

**Step 2: Review and Remove Public Bucket Policy**
```bash
aws s3api delete-bucket-policy --bucket BUCKET_NAME
```

**Step 3: Verify Fix**
```bash
aws s3api get-public-access-block --bucket BUCKET_NAME
```

**Terraform Fix:**
```hcl
resource "aws_s3_bucket_public_access_block" "secure" {
  bucket = aws_s3_bucket.example.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```
"""
    }
]

def generate_remediation_prompt(finding: Dict) -> str:
    """
    Generate LLM prompt for remediation guidance
    
    Args:
        finding: Dict with finding details
    
    Returns:
        Formatted prompt string
    """
    prompt = f"""{BASE_SYSTEM_PROMPT}

## Security Finding Details

**Finding ID**: {finding.get('finding_id', 'N/A')}
**Check**: {finding.get('check_title', 'N/A')}
**Service**: {finding.get('service', 'N/A')}
**Resource**: {finding.get('resource', 'N/A')}
**Severity**: {finding.get('severity', 'N/A')}
**ML Risk Priority**: {finding.get('ml_risk_priority', 'N/A')}
**Confidence**: {finding.get('ml_confidence', 0):.2%}

**Risk Description**:
{finding.get('risk', 'No description provided')}

**Compliance Impact**:
{', '.join(finding.get('compliance', {}).keys()) if finding.get('compliance') else 'None specified'}

## Task

Provide comprehensive remediation guidance for this security finding. Include:

1. **Immediate Actions**: Quick fixes to reduce risk
2. **Step-by-Step Remediation**: Detailed instructions with AWS CLI commands
3. **Console Instructions**: Manual steps via AWS Console
4. **Terraform Code**: Infrastructure-as-code fix
5. **Verification Steps**: How to confirm the fix worked
6. **Prevention**: How to prevent this misconfiguration in the future
7. **Compliance Notes**: How this fix addresses compliance requirements

Format your response in Markdown with clear sections and code blocks.
"""
    
    return prompt

def generate_bulk_remediation_prompt(findings: list[Dict], max_findings: int = 10) -> str:
    """
    Generate prompt for bulk remediation guidance
    
    Args:
        findings: List of finding dicts
        max_findings: Maximum findings to include
    
    Returns:
        Formatted prompt string
    """
    findings_summary = findings[:max_findings]
    
    prompt = f"""{BASE_SYSTEM_PROMPT}

## Multiple Security Findings

You have {len(findings_summary)} high-priority security findings to remediate:

"""
    
    for idx, finding in enumerate(findings_summary, 1):
        prompt += f"""
### Finding {idx}: {finding.get('check_title', 'Unknown')}
- **Service**: {finding.get('service', 'N/A')}
- **Resource**: {finding.get('resource', 'N/A')}
- **Severity**: {finding.get('severity', 'N/A')}
- **Risk**: {finding.get('risk', 'N/A')[:100]}...

"""
    
    prompt += """
## Task

Provide a prioritized remediation plan that:
1. Groups related findings that can be fixed together
2. Identifies dependencies between remediations
3. Suggests an optimal order of operations
4. Provides batch remediation scripts where possible
5. Highlights any risks of conflicts between fixes

For each group, provide consolidated remediation guidance.
"""
    
    return prompt
