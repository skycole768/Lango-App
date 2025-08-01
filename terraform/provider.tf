terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Adjust if using a specific version
    }
  }

  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}
