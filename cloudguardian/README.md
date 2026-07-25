# CloudGuardian - AI-Driven Cloud Misconfiguration Detection and Remediation

[![AWS](https://img.shields.io/badge/AWS-Cloud%20Security-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)](https://www.terraform.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 Project Overview

CloudGuardian is an automated **Cloud Security Posture Management (CSPM)** system that detects, prioritizes, and remediates AWS cloud misconfigurations using:
- **ML-based risk prioritization** (Random Forest classifier)
- **LLM-powered remediation guidance** (GPT-5.2/Claude via Emergent Universal Key)
- **Automated remediation** (AWS Lambda with safety guardrails)
- **Compliance mapping** (ISO 27001:2022, DPDP Act 2023, HIPAA, PCI-DSS)

**Team Members:** 4  
**AWS Account:** Cloud_Guard (782700525901)  
**Mode:** Team Project (12+ misconfigurations, 4 Lambda functions, 4 compliance frameworks)

---

## 📁 Repository Structure

```
cloudguardian/
├── infrastructure/           # Terraform IaC for AWS workload
├── misconfigurations/        # Intentional misconfiguration catalog
├── cspm-scans/              # CSPM scanning tools (Prowler, Steampipe, ScoutSuite)
├── ml-prioritization/        # ML risk scoring model
├── llm-remediation/         # LLM-powered remediation guidance
├── auto-remediation/        # AWS Lambda functions with guardrails
├── compliance/              # Compliance framework mappings
├── reports/                 # Project deliverables and findings
├── scripts/                 # Automation utilities
├── tests/                   # Unit and integration tests
├── config/                  # Configuration files
├── docs/                    # Documentation
└── presentation/            # Oral defense materials
```

---

## 🚀 Quick Start

### Prerequisites
- AWS Account (Free Tier)
- Python 3.9+
- Terraform 1.5+
- AWS CLI configured
- Docker (optional, for CSPM tools)

### Setup

```bash
# 1. Clone repository
cd cloudguardian

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure AWS credentials
aws configure
# Account ID: 782700525901

# 4. Deploy infrastructure
cd infrastructure
terraform init
terraform plan
terraform apply

# 5. Run CSPM scans
cd ../cspm-scans
./scripts/run-all-scans.sh

# 6. Consolidate findings
python consolidated/consolidate-findings.py

# 7. Run ML prioritization
cd ../ml-prioritization
jupyter notebook notebooks/ml-prioritization-model.ipynb

# 8. Generate LLM remediation guidance
cd ../llm-remediation
python src/generate_guidance.py

# 9. Deploy auto-remediation Lambda functions
cd ../auto-remediation
./deploy-lambda.sh
```

---

## 🔍 Key Features

### 1. Infrastructure Deployment
- **Terraform IaC** for reproducible AWS environment
- **12+ intentional misconfigurations** for detection testing
- Multi-tier architecture (VPC, EC2, RDS, S3, IAM)

### 2. Multi-Tool CSPM Scanning
- **Prowler**: Primary AWS security assessment
- **Steampipe**: SQL-based compliance checks
- **ScoutSuite**: Cross-validation and gap analysis

### 3. ML Risk Prioritization
- Feature engineering: severity, resource type, exploitability, blast radius
- Random Forest classifier with 85%+ accuracy
- Risk scores: Critical, High, Medium, Low

### 4. LLM Remediation Guidance
- **Emergent Universal LLM Key** (free, supports GPT-5.2 & Claude)
- Context-aware remediation steps
- Verification logic for accuracy
- Human-readable and machine-executable formats

### 5. Automated Remediation
- **4 Lambda functions** with safety guardrails:
  - S3 public access blocking
  - IAM MFA enforcement
  - EBS encryption enablement
  - Security group hardening
- Pre-checks and post-checks
- Approval workflow integration

### 6. Compliance Mapping
- ISO 27001:2022 Annex A controls
- DPDP Act 2023 (India Data Protection)
- HIPAA (Healthcare)
- PCI-DSS v4.0 (Payment Card Industry)

---

## 📊 Deliverables

### Code & Configuration
- ✅ Terraform infrastructure code
- ✅ CSPM scanning scripts
- ✅ ML model (Jupyter notebook + trained model)
- ✅ LLM integration with verification
- ✅ 4 Lambda functions with guardrails
- ✅ Compliance crosswalk tables

### Documentation
- ✅ Written report (14-18 pages for team)
- ✅ Architecture diagrams
- ✅ Setup and user guides
- ✅ Ethical considerations
- ✅ Oral defense presentation

---

## 🛡️ Security & Ethics

- **Responsible AI**: All LLM interactions logged and verified
- **Data Privacy**: No sensitive data sent to LLMs (redacted credentials)
- **Safety Guardrails**: Pre-checks, post-checks, approval workflows
- **Least Privilege**: IAM roles with minimal permissions
- **Lab Environment**: Intentional misconfigurations in isolated environment

---

## 👥 Team

**Team Size:** 4 members  
**Project Mode:** Team  
**Workload Distribution:** See `docs/team-contribution-matrix.md`

---

## 📚 Documentation

- [Architecture Diagram](docs/architecture/architecture-diagram.md)
- [Setup Guide](docs/setup-guide.md)
- [User Manual](docs/user-manual.md)
- [Compliance Mapping Guide](docs/compliance-mapping-guide.md)
- [API Documentation](docs/api-documentation.md)

---

## 🔗 Resources

- [Prowler Documentation](https://github.com/prowler-cloud/prowler)
- [Steampipe AWS Compliance](https://hub.steampipe.io/mods/turbot/aws_compliance)
- [ScoutSuite](https://github.com/nccgroup/ScoutSuite)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [ISO 27001:2022](https://www.iso.org/standard/27001)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

This is an academic capstone project. For questions or collaboration, please contact the team.

---

**Built with ❤️ for Cloud Security**
