# CloudGuardian - Product Requirements Document (PRD)

## Original Problem Statement

**Project**: CloudGuardian - AI-Driven Cloud Misconfiguration Detection and Remediation

An automated Cloud Security Posture Management (CSPM) system that detects, prioritizes, and remediates AWS cloud misconfigurations using:
- ML-based risk prioritization
- LLM-powered remediation guidance
- Automated remediation via AWS Lambda
- Compliance mapping (ISO 27001, DPDP, HIPAA, PCI-DSS)

## User Choices Confirmed

- **LLM API**: Emergent Universal LLM Key (Free) - Supports GPT-5.2 & Claude Sonnet 4.6
- **AWS Account**: Cloud_Guard (782700525901), Root access, ACTIVE
- **Project Scope**: Team Mode (4 members)
- **Repository Structure**: Option C - CloudGuardian as subdirectory (`/app/cloudguardian/`)
- **Existing Files**: Placeholders created for user upload

## Architecture

### Layer 1: Infrastructure (Terraform)
- VPC with public/private subnets
- EC2 instances (t2.micro, Free Tier)
- RDS MySQL (db.t2.micro, Free Tier)
- S3 buckets (3 buckets with various configurations)
- IAM users, roles, policies
- Security groups
- CloudTrail
- **14 intentional misconfigurations** for CSPM testing

### Layer 2: Detection (CSPM Tools)
- **Prowler** - Primary AWS security scanner
- **Steampipe** - SQL-based compliance checks
- **ScoutSuite** - Cross-validation
- **Consolidation script** - Python normalization

### Layer 3: Prioritization (ML)
- Random Forest Classifier
- 8 engineered features
- Target: CRITICAL/HIGH/MEDIUM/LOW priority
- Target accuracy: 85%+

### Layer 4: Remediation (LLM)
- Emergent Universal LLM Key
- GPT-5.2 / Claude Sonnet 4.6
- Context-aware guidance
- Verification logic
- Multi-format outputs

### Layer 5: Automation (Lambda)
- 4 Lambda functions:
  1. S3 Public Access Remediation
  2. IAM MFA Enforcement
  3. EBS Encryption
  4. Security Group Hardening
- Safety guardrails (pre/post checks, approval workflow)
- EventBridge triggers

### Layer 6: Compliance
- ISO 27001:2022 mapping
- DPDP Act 2023 mapping
- HIPAA mapping
- PCI-DSS v4.0 mapping
- Automated report generation

## What's Been Implemented (2026-01-25)

### Complete Directory Structure
```
/app/cloudguardian/
├── README.md, LICENSE, .gitignore, requirements.txt
├── infrastructure/         # Terraform IaC (main.tf, vpc.tf, ec2.tf, rds.tf, s3.tf, iam.tf, security-groups.tf, cloudtrail.tf)
├── misconfigurations/      # Catalog of 14 misconfigurations + injection script
├── cspm-scans/            # Prowler, Steampipe scripts + consolidation
├── ml-prioritization/      # Random Forest model with training/prediction scripts + Jupyter notebook
├── llm-remediation/        # Emergent LLM Key integration with prompts
├── auto-remediation/       # 4 Lambda functions with guardrails + Terraform deployment
├── compliance/             # 4 framework crosswalks + report generator
├── reports/                # Report templates + ethical considerations
├── scripts/                # Setup + full pipeline scripts
├── tests/                  # Unit tests for consolidation, ML, remediation
├── config/                 # AWS + CSPM configuration YAMLs
├── docs/                   # Setup guide + architecture diagrams
└── presentation/           # Slide structure + Q&A preparation
```

### Files Created
- **18 Python files**: Consolidation, ML training/prediction, LLM integration, Lambda handlers, tests
- **13 Terraform files**: Complete infrastructure + Lambda deployment
- **19 Markdown files**: Comprehensive documentation
- **4 CSV compliance crosswalks**: ISO 27001, DPDP, HIPAA, PCI-DSS
- **1 Jupyter notebook**: ML model development
- **Multiple shell scripts**: Setup, pipeline execution, deployment

### Features Implemented
1. **Terraform Infrastructure**: Complete AWS resource definitions with 14 intentional misconfigurations
2. **CSPM Consolidation**: Python script that normalizes findings from Prowler + Steampipe
3. **ML Model**: Random Forest classifier with feature engineering
4. **LLM Integration**: EmergentLLMClient class using Emergent Universal Key (GPT-5.2)
5. **4 Lambda Functions**: Complete handler code with safety guardrails
6. **Compliance Reports**: Automated crosswalk generation and reporting
7. **Documentation**: Setup guide, architecture diagrams, ethical considerations

## Prioritized Backlog

### P0 - Critical (Not yet implemented)
- [ ] User needs to upload existing files (project guide PDF, baseline reports, XLSX mappings)
- [ ] Deploy actual AWS infrastructure via Terraform (requires AWS credentials)
- [ ] Run actual CSPM scans on deployed infrastructure
- [ ] Train ML model with real findings

### P1 - High Priority
- [ ] Complete Jupyter notebook with actual training run
- [ ] Test LLM integration with real Emergent API key
- [ ] Deploy Lambda functions to AWS
- [ ] Generate initial compliance report
- [ ] Write actual content for final report sections (currently templates)

### P2 - Medium Priority
- [ ] Create actual PDF presentation slides
- [ ] Record demo videos
- [ ] Complete integration tests
- [ ] Set up GitHub Actions CI/CD
- [ ] Add more Steampipe custom queries

### P3 - Nice to Have
- [ ] Multi-region support
- [ ] Multi-account support
- [ ] Web dashboard for findings visualization
- [ ] Slack/Teams integration for notifications
- [ ] Custom Prowler check development

## Next Action Items

### For User
1. **Upload existing files** to placeholders:
   - Project guide PDF → `docs/project-guide/`
   - Prowler baseline HTML → `reports/` and `cspm-scans/prowler/outputs/`
   - Excel compliance mappings → `compliance/mappings/`

2. **Deploy AWS infrastructure**:
   ```bash
   cd /app/cloudguardian/infrastructure
   terraform init
   terraform apply
   ```

3. **Run CSPM scans**:
   ```bash
   cd /app/cloudguardian/scripts
   bash run-full-pipeline.sh
   ```

4. **Write final report content**:
   - Fill in template sections in `reports/final-written-report-template.md`
   - Create PDF version

5. **Create presentation slides**:
   - Follow structure in `presentation/slides-structure.md`
   - Use Google Slides or PowerPoint

### For Next Session
1. Test full pipeline end-to-end
2. Fine-tune ML model with real data
3. Optimize LLM prompts based on outputs
4. Deploy and test Lambda functions
5. Generate final compliance report

## Technical Stack

- **Language**: Python 3.9+
- **IaC**: Terraform 1.7+
- **Cloud**: AWS (Free Tier)
- **ML**: scikit-learn 1.4+, pandas, numpy
- **LLM**: Emergent Universal Key (GPT-5.2, Claude Sonnet 4.6)
- **Serverless**: AWS Lambda (Python 3.9 runtime)
- **CSPM Tools**: Prowler 4.0+, Steampipe 0.21+, ScoutSuite 5.14+
- **Testing**: pytest, moto (AWS mocking)
- **Compliance**: ISO 27001:2022, DPDP Act 2023, HIPAA, PCI-DSS v4.0

## Success Metrics

- **Infrastructure**: 15+ AWS resources deployed
- **Detection**: 40+ unique findings identified
- **ML Accuracy**: 85%+ on test data
- **LLM Verification**: 95%+ pass rate
- **Auto-remediation**: 4 Lambda functions operational
- **Compliance Coverage**: 200+ controls mapped
- **Cost**: $0 (Free Tier + Emergent Universal Key)

## Team Structure (4 members)

- **Member 1**: Infrastructure & Terraform, ISO 27001 mapping
- **Member 2**: CSPM scanning & consolidation, DPDP Act mapping
- **Member 3**: ML model development, HIPAA mapping
- **Member 4**: LLM integration & Lambda functions, PCI-DSS mapping
- **Shared**: Testing, documentation, report writing, presentation

---

**Last Updated**: 2026-01-25  
**Status**: Structure and code complete. Awaiting user file uploads and AWS deployment.
