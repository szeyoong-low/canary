terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.58"
    }

    tfe = {
      source  = "hashicorp/tfe"
      version = "~> 0.80"
    }

    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.24"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.14"
    }
  }

  required_version = "~> 1.15"

  // GitHub Actions does not invoke the Terraform binary, so the Terraform files
  // are not parsed. Pass as environment vars through GitHub CLI or workflow config.
  // This block allows local runs to be executed remotely against the HCP workspace 
  cloud {
    organization = "CanaryMarkets"

    workspaces {
      project = "Canary"
      name    = "production" // Just a placeholder. Set `TF_WORKSPACE` in HCP
    }
  }
}
