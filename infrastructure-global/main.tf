provider "aws" {
  region = "eu-west-2" // London

  default_tags {
    tags = {
      managed_via = "terraform"
      environment = local.environment // `environment` is load-bearing: used for ABAC
    }
  }
}

locals {
  environment = "global"

  // Owns the canary.markets domain
  cloudflare_zone_id = "298ffd9b0153fe3a36795cda6401f8e9"

  // Owns the zone and the Workers
  cloudflare_account_id = "186e5cb41a4496f3fe4621133cbfb8b6"
}
