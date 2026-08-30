terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.58"
    }
  }

  required_version = "~> 1.15"

  # Workspace runs are to be triggered via the CLI, not GitHub Actions
  cloud {
    organization = "CanaryMarkets"

    workspaces {
      project = "Canary"
      name    = "bootstrap"
    }
  }
}
