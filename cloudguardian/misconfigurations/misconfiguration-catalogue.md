# CloudGuardian Misconfiguration Catalogue
## Team Mode: 12+ Intentional Security Misconfigurations

### Overview
This document catalogs all intentional security misconfigurations introduced into the CloudGuardian AWS infrastructure for CSPM detection testing and ML model training.

---

## Misconfiguration List

### 1. S3 Bucket Public Access (S3-001)
**Resource**: `cloudguardian-lab-data-1-*` S3 bucket  
**Severity**: CRITICAL  
**Description**: S3 bucket has public access block disabled, allowing public read/write access  
**Risk**: Data exposure, unauthorized data modification, data exfiltration  
**Compliance Impact**:
- ISO 27001:2022: A.8.2 (Information classification)
- DPDP Act 2023: Section 8 (Security safeguards)
- HIPAA: §164.308(a)(3) (Workforce Security)
- PCI-DSS: Requirement 1.2.1 (Restrict inbound/outbound traffic)

**Detection**: Prowler check `s3_bucket_public_access`

---

### 2. Security Group SSH from Anywhere (SG-001)
**Resource**: Web tier security group  
**Severity**: HIGH  
**Description**: SSH port (22) open to 0.0.0.0/0  
**Risk**: Brute force attacks, unauthorized access, lateral movement  
**Compliance Impact**:
- ISO 27001:2022: A.8.20 (Networks controls)
- HIPAA: §164.312(a)(1) (Access Control)
- PCI-DSS: Requirement 1.3 (Prohibit direct public access)

**Detection**: Prowler check `ec2_securitygroup_allow_ingress_from_internet_to_any_port`

---

### 3. Security Group MySQL from Anywhere (SG-002)
**Resource**: Database security group  
**Severity**: CRITICAL  
**Description**: MySQL port (3306) open to 0.0.0.0/0  
**Risk**: Database compromise, data breach, SQL injection exploitation  
**Compliance Impact**:
- ISO 27001:2022: A.8.20 (Networks controls)
- DPDP Act 2023: Section 8 (Security safeguards)
- HIPAA: §164.312(a)(1) (Access Control)
- PCI-DSS: Requirement 1.3

**Detection**: Prowler check `ec2_securitygroup_allow_ingress_from_internet_to_any_port`

---

### 4. Unencrypted EBS Volumes (EC2-001)
**Resource**: EC2 instance root volumes  
**Severity**: HIGH  
**Description**: EBS volumes not encrypted at rest  
**Risk**: Data exposure if volume accessed by unauthorized party  
**Compliance Impact**:
- ISO 27001:2022: A.8.24 (Use of cryptography)
- DPDP Act 2023: Section 8 (Security safeguards)
- HIPAA: §164.312(a)(2)(iv) (Encryption)
- PCI-DSS: Requirement 3.4 (Render PAN unreadable)

**Detection**: Prowler check `ec2_ebs_volume_encryption`

---

### 5. RDS Publicly Accessible (RDS-001)
**Resource**: MySQL RDS instance  
**Severity**: CRITICAL  
**Description**: RDS instance has public accessibility enabled  
**Risk**: Database exposed to internet, unauthorized access  
**Compliance Impact**:
- ISO 27001:2022: A.8.20 (Networks controls)
- DPDP Act 2023: Section 8
- HIPAA: §164.312(a)(1)
- PCI-DSS: Requirement 1.3

**Detection**: Prowler check `rds_instance_publicly_accessible`

---

### 6. RDS Automated Backups Disabled (RDS-002)
**Resource**: MySQL RDS instance  
**Severity**: MEDIUM  
**Description**: Automated backup retention period set to 0  
**Risk**: Data loss, no point-in-time recovery  
**Compliance Impact**:
- ISO 27001:2022: A.8.13 (Information backup)
- HIPAA: §164.308(a)(7)(ii)(A) (Data Backup Plan)
- PCI-DSS: Requirement 3.1 (Data retention)

**Detection**: Prowler check `rds_instance_backup_enabled`

---

### 7. RDS Storage Not Encrypted (RDS-003)
**Resource**: MySQL RDS instance  
**Severity**: HIGH  
**Description**: RDS storage encryption disabled  
**Risk**: Data at rest exposed  
**Compliance Impact**:
- ISO 27001:2022: A.8.24
- DPDP Act 2023: Section 8
- HIPAA: §164.312(a)(2)(iv)
- PCI-DSS: Requirement 3.4

**Detection**: Prowler check `rds_instance_storage_encrypted`

---

### 8. S3 Versioning Disabled (S3-002)
**Resource**: All data S3 buckets  
**Severity**: MEDIUM  
**Description**: S3 bucket versioning not enabled  
**Risk**: Accidental deletion, no version history  
**Compliance Impact**:
- ISO 27001:2022: A.8.13 (Information backup)
- PCI-DSS: Requirement 10.5.3 (File integrity monitoring)

**Detection**: Prowler check `s3_bucket_versioning_enabled`

---

### 9. S3 Bucket Unencrypted (S3-003)
**Resource**: First S3 data bucket  
**Severity**: HIGH  
**Description**: S3 bucket lacks server-side encryption  
**Risk**: Data at rest exposed  
**Compliance Impact**:
- ISO 27001:2022: A.8.24
- DPDP Act 2023: Section 8
- HIPAA: §164.312(a)(2)(iv)
- PCI-DSS: Requirement 3.4

**Detection**: Prowler check `s3_bucket_default_encryption`

---

### 10. S3 Access Logging Disabled (S3-004)
**Resource**: All data S3 buckets  
**Severity**: MEDIUM  
**Description**: S3 bucket access logging not configured  
**Risk**: No audit trail for data access  
**Compliance Impact**:
- ISO 27001:2022: A.8.15 (Logging)
- HIPAA: §164.312(b) (Audit Controls)
- PCI-DSS: Requirement 10.1 (Audit trails)

**Detection**: Prowler check `s3_bucket_server_access_logging_enabled`

---

### 11. IAM Policy Wildcard Permissions (IAM-001)
**Resource**: Team member IAM policies  
**Severity**: HIGH  
**Description**: IAM policies use wildcard (*) for actions and resources  
**Risk**: Excessive permissions, privilege escalation  
**Compliance Impact**:
- ISO 27001:2022: A.5.15 (Access control)
- HIPAA: §164.308(a)(4) (Information Access Management)
- PCI-DSS: Requirement 7.1 (Limit access to least privilege)

**Detection**: Prowler check `iam_policy_attached_only_to_group_or_roles`

---

### 12. IAM Access Keys Not Rotated (IAM-002)
**Resource**: Team member IAM users  
**Severity**: MEDIUM  
**Description**: IAM access keys never rotated  
**Risk**: Compromised credentials, unauthorized access  
**Compliance Impact**:
- ISO 27001:2022: A.5.17 (Authentication information)
- HIPAA: §164.308(a)(5)(ii)(D) (Password Management)
- PCI-DSS: Requirement 8.2.4 (Change passwords quarterly)

**Detection**: Prowler check `iam_user_accesskey_unused`

---

### 13. CloudTrail Single Region (TRAIL-001)
**Resource**: CloudTrail trail  
**Severity**: MEDIUM  
**Description**: CloudTrail not configured for multi-region  
**Risk**: Incomplete audit trail, blind spots  
**Compliance Impact**:
- ISO 27001:2022: A.8.15 (Logging)
- HIPAA: §164.312(b) (Audit Controls)
- PCI-DSS: Requirement 10.1

**Detection**: Prowler check `cloudtrail_multi_region_enabled`

---

### 14. CloudTrail Log Validation Disabled (TRAIL-002)
**Resource**: CloudTrail trail  
**Severity**: MEDIUM  
**Description**: CloudTrail log file validation not enabled  
**Risk**: Log tampering, integrity compromise  
**Compliance Impact**:
- ISO 27001:2022: A.8.15 (Logging)
- HIPAA: §164.312(c)(1) (Integrity)
- PCI-DSS: Requirement 10.5 (Secure audit trails)

**Detection**: Prowler check `cloudtrail_log_file_validation_enabled`

---

## Summary Statistics

- **Total Misconfigurations**: 14
- **Critical Severity**: 3
- **High Severity**: 5
- **Medium Severity**: 6
- **Affected Services**: S3, EC2, RDS, IAM, CloudTrail, Security Groups

## Remediation Priority

### Immediate (Critical)
1. S3-001: Block public access
2. SG-002: Restrict MySQL access
3. RDS-001: Disable public accessibility

### High Priority
4. SG-001: Restrict SSH access
5. EC2-001: Enable EBS encryption
6. RDS-003: Enable RDS encryption
7. S3-003: Enable S3 encryption
8. IAM-001: Remove wildcard permissions

### Medium Priority
9. RDS-002: Enable automated backups
10. S3-002: Enable versioning
11. S3-004: Enable access logging
12. IAM-002: Rotate access keys
13. TRAIL-001: Enable multi-region
14. TRAIL-002: Enable log validation

---

**Last Updated**: 2026-01-25  
**Team**: CloudGuardian CSPM Team (4 members)  
**AWS Account**: Cloud_Guard (782700525901)
