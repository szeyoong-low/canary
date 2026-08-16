terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.58"
    }
  }

  required_version = "~> 1.15"

  cloud {
    organization = "CanaryMarkets"

    workspaces {
      project = "Canary"
      // `TF_WORKSPACE` must be set
    }
  }
}
