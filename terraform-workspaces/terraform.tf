terraform {
  required_providers {
    tfe = {
      source  = "hashicorp/tfe"
      version = "~> 0.80.0"
    }
  }

  required_version = "~> 1.15"

  cloud {
    organization = "CanaryMarkets"

    workspaces {
      project = "Canary"
      name    = "workspace-manager"
    }
  }
}
