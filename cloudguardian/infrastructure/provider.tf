# CloudGuardian Terraform Provider Configuration
# AWS Account: Cloud_Guard (782700525901)

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  
  # Optional: Remote state backend
  # backend "s3" {
  #   bucket = "cloudguardian-terraform-state"
  #   key    = "cloudguardian/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region
  
  # AWS Account ID validation
  allowed_account_ids = ["782700525901"]
  
  default_tags {
    tags = {
      Project     = "CloudGuardian"
      Environment = "Lab"
      Team        = "CSPM-Team"
      ManagedBy   = "Terraform"
      Purpose     = "Capstone-Security-Research"
    }
  }
}

provider "random" {}
