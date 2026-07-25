# CloudGuardian System Architecture

## High-Level Architecture

```
┌────────────────────────────────────┐
│   AWS Infrastructure (Cloud_Guard)    │
│   Account ID: 782700525901            │
│                                        │
│  ┌────────────────────────────┐  │
│  │ VPC (10.0.0.0/16)           │  │
│  │  - EC2 Instances (t2.micro)  │  │
│  │  - RDS MySQL (db.t2.micro)   │  │
│  │  - S3 Buckets                │  │
│  │  - IAM Users/Roles           │  │
│  │  - Security Groups           │  │
│  │  - CloudTrail                │  │
│  └────────────────────────────┘  │
│          │                           │
│          ↓ (Scan)                   │
└────────────────────────────────────┘
           │
           ↓
┌────────────────────────────────────┐
│      CSPM Scanning Layer          │
│                                    │
│  ┌─────────┐  ┌──────────┐  │
│  │ Prowler │  │ Steampipe│  │
│  │  4.0+   │  │   0.21+  │  │
│  └─────────┘  └──────────┘  │
│          │          │           │
│          └──────────┘           │
│                 ↓                  │
│        Consolidation Script        │
│       (Python - Normalize)         │
└────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│    ML Risk Prioritization         │
│                                    │
│  Random Forest Classifier        │
│  - Severity scoring              │
│  - Exploitability analysis       │
│  - Blast radius calculation      │
│  - Compliance impact             │
│                                    │
│  Output: Prioritized Findings    │
└────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│    LLM Remediation Guidance       │
│                                    │
│  Emergent Universal LLM Key      │
│  - GPT-5.2 / Claude Sonnet 4.6  │
│  - Prompt engineering            │
│  - Context-aware remediation     │
│  - Verification logic            │
│                                    │
│  Output: Remediation Steps       │
└────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ↓                 ↓
┌────────────┐    ┌──────────────────┐
│   Manual    │    │ Auto-Remediation │
│Remediation │    │   (AWS Lambda)   │
│ (Human)    │    │                  │
│            │    │  4 Functions:   │
│ - Review   │    │  1. S3 Public   │
│ - Execute  │    │  2. IAM MFA     │
│ - Verify   │    │  3. EBS Encrypt │
│            │    │  4. SG Harden   │
└────────────┘    └──────────────────┘
        │                 │
        └────────┬────────┘
                 │
                 ↓
┌────────────────────────────────────┐
│    Compliance Reporting           │
│                                    │
│  - ISO 27001:2022                │
│  - DPDP Act 2023                 │
│  - HIPAA                         │
│  - PCI-DSS v4.0                  │
│                                    │
│  Output: Compliance Reports      │
└────────────────────────────────────┘
```

## Component Details

### 1. Infrastructure Layer (Terraform)
- **Purpose**: Deploy AWS workload with intentional misconfigurations
- **Technology**: Terraform 1.5+
- **Resources**: VPC, EC2, RDS, S3, IAM, Security Groups, CloudTrail
- **Misconfigurations**: 14 intentional security issues

### 2. Detection Layer (CSPM Tools)
- **Prowler**: Primary AWS security scanner
- **Steampipe**: SQL-based compliance checks
- **ScoutSuite**: Cross-validation and gap analysis
- **Output**: JSON, CSV, HTML reports

### 3. Consolidation Layer (Python)
- **Purpose**: Normalize findings from multiple tools
- **Features**: Deduplication, schema normalization, enrichment
- **Output**: Unified findings database (JSON/CSV)

### 4. ML Prioritization (scikit-learn)
- **Model**: Random Forest Classifier
- **Features**: 8 engineered features
- **Output**: Risk priority (CRITICAL/HIGH/MEDIUM/LOW)
- **Accuracy Target**: 85%+

### 5. LLM Remediation (Emergent Universal Key)
- **Provider**: GPT-5.2 or Claude Sonnet 4.6
- **Purpose**: Generate context-aware remediation guidance
- **Features**: Prompt engineering, verification, multi-format output
- **Privacy**: Sensitive data redacted

### 6. Auto-Remediation (AWS Lambda)
- **Functions**: 4 Lambda functions for common fixes
- **Triggers**: EventBridge rules
- **Safety**: Pre-checks, post-checks, approval workflows
- **Monitoring**: CloudWatch Logs and Metrics

### 7. Compliance Mapping
- **Frameworks**: ISO 27001, DPDP, HIPAA, PCI-DSS
- **Method**: Crosswalk tables mapping findings to controls
- **Output**: Gap analysis and compliance reports

## Data Flow

1. **Infrastructure Deployment**: Terraform creates AWS resources with misconfigurations
2. **CSPM Scanning**: Prowler, Steampipe scan AWS account
3. **Consolidation**: Python script normalizes findings
4. **ML Prioritization**: Random Forest model assigns risk scores
5. **LLM Guidance**: Emergent LLM generates remediation steps
6. **Remediation**: Lambda functions or manual execution
7. **Compliance**: Map findings to frameworks, generate reports
8. **Verification**: Re-scan to confirm fixes

## Technology Stack

- **Cloud**: AWS (Free Tier)
- **IaC**: Terraform 1.5+
- **Language**: Python 3.9+
- **ML**: scikit-learn, pandas, numpy
- **LLM**: Emergent Universal Key (GPT-5.2/Claude)
- **Serverless**: AWS Lambda
- **Monitoring**: CloudWatch
- **CI/CD**: (Optional) GitHub Actions

## Security Considerations

- **Least Privilege**: All IAM roles use minimal permissions
- **Data Privacy**: No sensitive data sent to external LLMs
- **Audit Trail**: All actions logged to CloudTrail
- **Encryption**: KMS encryption for sensitive data
- **Network Isolation**: Lambda functions in VPC

## Scalability

- **Current**: Single AWS account, us-east-1
- **Future**: Multi-account, multi-region support
- **Findings**: Designed to handle 1000+ findings
- **Lambda**: Auto-scaling to handle spikes

---

**Last Updated**: 2026-01-25
**Team**: CloudGuardian (4 members)
**AWS Account**: Cloud_Guard (782700525901)
