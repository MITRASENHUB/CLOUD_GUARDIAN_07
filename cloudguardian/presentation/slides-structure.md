# CloudGuardian Presentation Slides Structure

**Total Duration**: 15-20 minutes  
**Format**: PDF slides + Live Demo  
**Team**: 4 members (each presents section)

## Slide Structure (20-25 slides)

### Section 1: Introduction (3 slides, Member 1 - 2 min)

**Slide 1: Title Slide**
- CloudGuardian: AI-Driven Cloud Misconfiguration Detection and Remediation
- Team Members: Name, Name, Name, Name
- Date, Course, University

**Slide 2: The Problem**
- Cloud misconfigurations = 70% of breaches
- Traditional CSPM = alert fatigue
- Remediation is slow and error-prone
- Compliance is fragmented

**Slide 3: Our Solution**
- Multi-tool CSPM (Prowler + Steampipe + ScoutSuite)
- ML-based risk prioritization
- LLM-powered remediation guidance
- Automated Lambda remediation
- Multi-framework compliance mapping

---

### Section 2: Architecture (3 slides, Member 1 - 3 min)

**Slide 4: System Architecture**
- High-level diagram
- Show data flow from AWS to remediation

**Slide 5: Technology Stack**
- AWS (Free Tier): EC2, RDS, S3, IAM, Lambda
- Terraform for IaC
- Python 3.9+
- ML: scikit-learn
- LLM: Emergent Universal Key (GPT-5.2/Claude)

**Slide 6: Development Approach**
- Team collaboration (4 members)
- GitHub for version control
- Test-driven development
- Continuous integration

---

### Section 3: Infrastructure & Misconfigurations (3 slides, Member 1 - 2 min)

**Slide 7: Infrastructure Deployment**
- Multi-tier architecture
- 15+ AWS resources
- Terraform code snippets
- Deployment metrics

**Slide 8: Intentional Misconfigurations (14+)**
- Table showing all misconfigurations
- Grouped by service (S3, EC2, RDS, IAM, etc.)
- Severity distribution

**Slide 9: Live Demo #1**
- Terraform apply
- Show AWS Console
- Highlight misconfigurations

---

### Section 4: Detection Layer (2 slides, Member 2 - 2 min)

**Slide 10: CSPM Tool Comparison**
- Prowler vs Steampipe vs ScoutSuite
- Coverage and unique features
- Why we used all three

**Slide 11: Findings Consolidation**
- Normalization approach
- Deduplication logic
- Findings statistics (50+ detected)

---

### Section 5: ML Risk Prioritization (3 slides, Member 3 - 3 min)

**Slide 12: ML Model Design**
- Feature engineering (8 features)
- Random Forest classifier
- Class distribution

**Slide 13: Model Performance**
- 85%+ accuracy
- Confusion matrix
- Feature importance chart
- Cross-validation scores

**Slide 14: Live Demo #2**
- Run predict.py
- Show prioritized findings
- Compare with rule-based approach

---

### Section 6: LLM Remediation (3 slides, Member 4 - 3 min)

**Slide 15: LLM Integration**
- Emergent Universal Key
- GPT-5.2 / Claude Sonnet 4.6
- Prompt engineering approach

**Slide 16: Verification & Safety**
- Multi-layer verification
- Data privacy (redaction)
- Human-in-the-loop
- Ethical considerations

**Slide 17: Live Demo #3**
- Generate remediation for a finding
- Show quality of output
- Highlight verification

---

### Section 7: Auto-Remediation (2 slides, Member 4 - 2 min)

**Slide 18: Lambda Functions**
- 4 functions with responsibilities:
  1. S3 Public Access
  2. IAM MFA
  3. EBS Encryption
  4. Security Group Hardening
- Safety guardrails

**Slide 19: EventBridge Automation**
- Real-time event-driven remediation
- Approval workflow
- CloudWatch monitoring

---

### Section 8: Compliance (2 slides, All members - 2 min)

**Slide 20: Compliance Mapping**
- 4 frameworks (ISO, DPDP, HIPAA, PCI-DSS)
- Crosswalk approach
- Coverage statistics

**Slide 21: Compliance Results**
- Before/after scores
- Gap analysis
- Priority recommendations

---

### Section 9: Results & Conclusion (3 slides, All - 2 min)

**Slide 22: Key Achievements**
- Metrics summary:
  - 14 misconfigurations detected
  - 85%+ ML accuracy
  - 95%+ LLM verification pass rate
  - 4 Lambda functions deployed
  - $0 total cost (Free Tier + Emergent Key)

**Slide 23: Future Work**
- Multi-cloud support
- Real-time threat detection
- Larger ML datasets
- Web UI
- SIEM/SOAR integration

**Slide 24: Q&A**
- Team contact info
- GitHub repository link
- Thank you slide

---

## Live Demo Plan (Backup: Pre-recorded video)

### Demo 1: Infrastructure & Misconfigurations (2 min)
1. Show Terraform apply
2. Navigate AWS Console
3. Highlight public S3 bucket
4. Show open SSH security group

### Demo 2: Detection & Prioritization (2 min)
1. Run Prowler scan (or show pre-recorded)
2. Show consolidation script output
3. Run ML prediction
4. Display prioritized findings

### Demo 3: Remediation (2 min)
1. Generate LLM guidance for top finding
2. Show quality of output
3. Trigger Lambda function
4. Verify remediation

---

## Speaker Assignments

| Section | Slides | Duration | Speaker |
|---------|--------|----------|---------|
| Introduction | 1-3 | 2 min | Member 1 |
| Architecture | 4-6 | 3 min | Member 1 |
| Infrastructure | 7-9 | 2 min | Member 1 |
| Detection | 10-11 | 2 min | Member 2 |
| ML Model | 12-14 | 3 min | Member 3 |
| LLM Remediation | 15-17 | 3 min | Member 4 |
| Auto-Remediation | 18-19 | 2 min | Member 4 |
| Compliance | 20-21 | 2 min | All (each covers 1 framework) |
| Conclusion | 22-24 | 2 min | Member 1 |
| Q&A | - | 5-10 min | All |

## Visual Design Guidelines

### Colors
- Primary: AWS Orange (#FF9900)
- Secondary: Dark Blue (#232F3E)
- Accent: Green (for success), Red (for issues)

### Typography
- Headings: Bold, sans-serif (Roboto, Open Sans)
- Body: Regular, readable size (24pt+)
- Code: Monospace (Courier, Consolas)

### Elements
- Consistent AWS icons for services
- Charts and graphs (avoid too much text)
- Screenshots of actual outputs
- Code snippets with syntax highlighting
- Team photo on title slide

## Presentation Checklist

### Content
- [ ] All 24 slides complete
- [ ] All demos tested and working
- [ ] Backup videos recorded
- [ ] Handouts prepared
- [ ] References list included

### Technical
- [ ] PDF version created
- [ ] Slides open in multiple software
- [ ] Fonts embedded
- [ ] Images high-resolution
- [ ] File size < 25MB

### Delivery
- [ ] Team practice sessions (3+ times)
- [ ] Time management (15-20 min)
- [ ] Q&A preparation
- [ ] Backup laptop ready
- [ ] USB drive with files

### Materials
- [ ] Business cards / contact info
- [ ] Printed handouts (optional)
- [ ] GitHub repo link
- [ ] Demo videos
- [ ] Q&A document

---

**Status**: Structure created. Actual slides need to be designed in PowerPoint/Keynote/Google Slides.

**Recommended Tool**: Google Slides (collaborative for team)  
**Alternative**: Canva (professional templates)
