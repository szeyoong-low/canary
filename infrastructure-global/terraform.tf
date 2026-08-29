terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.58"
    }

    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.24"
    }
  }

  required_version = "~> 1.15"

  cloud {
    organization = "CanaryMarkets"

    workspaces {
      project = "Canary"
      name    = "global"
    }
  }
}
