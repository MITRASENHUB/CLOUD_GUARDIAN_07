# CloudGuardian LLM Remediation System

This directory contains the LLM-powered remediation guidance system using **Emergent Universal LLM Key**.

## Overview

The LLM system generates context-aware remediation guidance for security findings using:
- **GPT-5.2** or **Claude Sonnet 4.6** (via Emergent Universal Key)
- Prompt engineering with few-shot examples
- Verification logic for accuracy
- Multi-format outputs (JSON, Markdown, executable scripts)

## Features

### 1. Context-Aware Remediation
- Analyzes finding details, resource context, and compliance requirements
- Generates step-by-step remediation instructions
- Provides both manual and automated remediation options

### 2. Emergent Universal Key Integration
- **Free LLM access** via Emergent Universal Key
- Supports GPT-5.2 (OpenAI) and Claude Sonnet 4.6 (Anthropic)
- No separate API keys needed
- Automatic rate limiting and retry logic

### 3. Verification System
- Validates LLM outputs against raw findings
- Checks for hallucinations and inaccuracies
- Confidence scoring for remediation steps

### 4. Multiple Output Formats
- **JSON**: Machine-readable for automation
- **Markdown**: Human-readable documentation
- **Bash/Python**: Executable remediation scripts
- **Terraform**: Infrastructure-as-code fixes

## Files

- `src/llm_client.py` - LLM API integration (Emergent Universal Key)
- `src/prompt_templates.py` - Prompt engineering templates
- `src/generate_guidance.py` - Main remediation generation script
- `src/verify_guidance.py` - Verification logic
- `prompts/base-prompt.txt` - Base prompt template
- `prompts/context-examples.txt` - Few-shot examples
- `config.yaml` - LLM configuration
- `outputs/remediation-guidance.json` - Generated guidance

## Quick Start

### 1. Set up Emergent Universal Key
```bash
# The key is automatically available in your environment
# No manual setup needed!
```

### 2. Generate Remediation Guidance
```bash
python src/generate_guidance.py
```

### 3. Review Outputs
```bash
cat outputs/remediation-guidance.md
```

## Configuration

Edit `config.yaml` to customize:
- LLM provider (GPT-5.2 or Claude Sonnet 4.6)
- Temperature and creativity settings
- Output formats
- Verification strictness

## Example Output

```markdown
### Remediation for S3-001: Public S3 Bucket

**Severity**: CRITICAL
**Resource**: cloudguardian-lab-data-1-abc123
**Risk**: Publicly accessible S3 bucket exposing sensitive data

#### Step 1: Block Public Access (Immediate)
```bash
aws s3api put-public-access-block \
  --bucket cloudguardian-lab-data-1-abc123 \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,\
    BlockPublicPolicy=true,RestrictPublicBuckets=true
```

#### Step 2: Review Bucket Policy
```bash
aws s3api get-bucket-policy --bucket cloudguardian-lab-data-1-abc123
```

#### Step 3: Enable Encryption
```bash
aws s3api put-bucket-encryption \
  --bucket cloudguardian-lab-data-1-abc123 \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

**Verification**: Run Prowler check to confirm fix
```bash
prowler aws --checks s3_bucket_public_access
```
```

## Usage Example

```python
from llm_client import EmergentLLMClient
from prompt_templates import generate_remediation_prompt

# Initialize client
client = EmergentLLMClient(provider='gpt-5.2')

# Load finding
finding = {
    'check_title': 'S3 bucket with public access',
    'service': 's3',
    'resource': 'cloudguardian-lab-data-1-abc123',
    'severity': 'CRITICAL',
    'risk': 'Publicly accessible bucket'
}

# Generate prompt
prompt = generate_remediation_prompt(finding)

# Get remediation guidance
response = client.generate(prompt)

print(response['remediation_steps'])
```

## Ethical Considerations

### Data Privacy
- **No sensitive data** sent to LLM (credentials, PII redacted)
- Resource IDs anonymized where possible
- All interactions logged for audit

### Verification
- All LLM outputs verified against raw findings
- Manual review required for high-impact remediations
- Confidence scores provided for each step

### Responsible AI
- Prompt templates designed to avoid harmful outputs
- Human-in-the-loop for critical operations
- Transparency in LLM limitations

## Next Steps

After generating remediation guidance:
1. Review outputs in `outputs/remediation-guidance.md`
2. Deploy Lambda functions for automated remediation
3. Generate compliance reports
