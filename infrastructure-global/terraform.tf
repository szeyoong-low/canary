terraform {
  required_providers {
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
