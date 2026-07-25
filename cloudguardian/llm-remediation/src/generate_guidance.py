#!/usr/bin/env python3
"""
CloudGuardian LLM Remediation Guidance Generator
Generates remediation guidance using Emergent Universal LLM Key
"""

import json
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from llm_client import EmergentLLMClient
from prompt_templates import generate_remediation_prompt, generate_bulk_remediation_prompt

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CONFIG_PATH = Path("./config.yaml")
INPUT_PATH = Path("./inputs/top-priority-findings.json")
OUTPUT_DIR = Path("./outputs")

OUTPUT_DIR.mkdir(exist_ok=True)

def load_config() -> Dict:
    """Load LLM configuration"""
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def load_findings() -> List[Dict]:
    """Load top priority findings from ML model"""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Priority findings not found at {INPUT_PATH}. "
            "Run ML prediction first: cd ../ml-prioritization && python src/predict.py"
        )
    
    with open(INPUT_PATH, 'r') as f:
        return json.load(f)

def redact_sensitive_data(finding: Dict) -> Dict:
    """Redact sensitive information before sending to LLM"""
    redacted = finding.copy()
    
    # Replace actual resource IDs with placeholders
    if 'resource' in redacted:
        # Keep resource type but anonymize specific IDs
        resource = redacted['resource']
        if '/' in resource:
            parts = resource.split('/')
            parts[-1] = 'RESOURCE_ID'
            redacted['resource'] = '/'.join(parts)
        elif '-' in resource and len(resource) > 20:
            redacted['resource'] = 'RESOURCE_NAME'
    
    return redacted

def generate_guidance_for_finding(client: EmergentLLMClient, finding: Dict) -> Dict:
    """
    Generate remediation guidance for a single finding
    
    Returns:
        Dict with remediation guidance and metadata
    """
    logger.info(f"Generating guidance for: {finding.get('check_title', 'Unknown')}")
    
    # Redact sensitive data
    redacted_finding = redact_sensitive_data(finding)
    
    # Generate prompt
    prompt = generate_remediation_prompt(redacted_finding)
    
    # Get LLM response
    response = client.generate_with_retry(prompt)
    
    # Structure output
    guidance = {
        'finding_id': finding.get('finding_id', 'unknown'),
        'check_title': finding.get('check_title', ''),
        'service': finding.get('service', ''),
        'resource': finding.get('resource', ''),
        'severity': finding.get('severity', ''),
        'ml_risk_priority': finding.get('ml_risk_priority', ''),
        'ml_confidence': finding.get('ml_confidence', 0),
        'remediation_guidance': response['content'],
        'llm_model': response['model'],
        'generated_at': datetime.now().isoformat(),
        'tokens_used': response.get('usage', {})
    }
    
    return guidance

def generate_markdown_report(guidance_list: List[Dict], output_path: Path):
    """Generate human-readable Markdown report"""
    md_content = f"""# CloudGuardian Remediation Guidance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Findings**: {len(guidance_list)}

---

"""
    
    for idx, guidance in enumerate(guidance_list, 1):
        md_content += f"""## {idx}. {guidance['check_title']}

**Service**: {guidance['service']}  
**Resource**: {guidance['resource']}  
**Severity**: {guidance['severity']}  
**ML Priority**: {guidance['ml_risk_priority']} (Confidence: {guidance['ml_confidence']:.1%})  
**Model**: {guidance['llm_model']}

{guidance['remediation_guidance']}

---

"""
    
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    logger.info(f"Markdown report saved to {output_path}")

def main():
    print("="*60)
    print("CloudGuardian LLM Remediation Guidance Generator")
    print("Using Emergent Universal LLM Key (Free)")
    print("="*60)
    
    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config()
    llm_config = config['llm']
    print(f"   Provider: {llm_config['provider']}")
    print(f"   Temperature: {llm_config['temperature']}")
    
    # Initialize LLM client
    print("\n2. Initializing Emergent LLM client...")
    client = EmergentLLMClient(
        provider=llm_config['provider'],
        temperature=llm_config['temperature']
    )
    print("   ✓ Client initialized")
    
    # Load findings
    print("\n3. Loading top priority findings...")
    findings = load_findings()
    print(f"   Loaded {len(findings)} findings")
    
    # Generate guidance for each finding
    print("\n4. Generating remediation guidance...")
    guidance_list = []
    
    for idx, finding in enumerate(findings[:10], 1):  # Limit to top 10
        print(f"   [{idx}/{min(10, len(findings))}] {finding.get('check_title', 'Unknown')[:50]}...")
        try:
            guidance = generate_guidance_for_finding(client, finding)
            guidance_list.append(guidance)
        except Exception as e:
            logger.error(f"Failed to generate guidance: {e}")
            continue
    
    print(f"   ✓ Generated guidance for {len(guidance_list)} findings")
    
    # Save outputs
    print("\n5. Saving outputs...")
    
    # JSON output
    json_path = OUTPUT_DIR / "remediation-guidance.json"
    with open(json_path, 'w') as f:
        json.dump(guidance_list, f, indent=2)
    print(f"   ✓ JSON saved to {json_path}")
    
    # Markdown report
    md_path = OUTPUT_DIR / "remediation-guidance.md"
    generate_markdown_report(guidance_list, md_path)
    print(f"   ✓ Markdown report saved to {md_path}")
    
    # Summary
    total_tokens = sum(g.get('tokens_used', {}).get('total_tokens', 0) for g in guidance_list)
    
    print("\n" + "="*60)
    print("✓ Remediation guidance generation complete!")
    print("="*60)
    print(f"\nFindings processed: {len(guidance_list)}")
    print(f"Total tokens used: {total_tokens:,}")
    print(f"\nOutputs:")
    print(f"  - JSON: {json_path}")
    print(f"  - Markdown: {md_path}")
    print(f"\nNext steps:")
    print(f"  1. Review guidance: cat {md_path}")
    print(f"  2. Deploy Lambda functions: cd ../auto-remediation")
    print()

if __name__ == "__main__":
    main()
