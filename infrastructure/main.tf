provider "aws" {
  region = "eu-west-2" // London

  default_tags {
    tags = {
      managed_by  = "terraform"
      environment = local.environment // `environment` is load-bearing: used for ABAC.
    }
  }
}

locals {
  // The HCP workspace this run belongs to: "production", "development-shared",
  // or "development-pr-n" for a pull request environment.
  workspace = terraform.workspace

  // Must stay identical to the "development-pr" environment key in
  // infrastructure-bootstrap, which is the principal tag carried by the OIDC role.
  development_pr_prefix = "development-pr"

  // The environment that attribute access control matches on. Exactly
  // three values are possible, and each must equal the `environment` tag on the
  // OIDC role this workspace assumes.
  // Every pull request shares one role, and so one principal tag.
  environment = startswith(local.workspace, local.development_pr_prefix) ? local.development_pr_prefix : local.workspace

  // is_prod = local.environment == "production"

  name_suffix = local.workspace // for global/regional/account-level uniqueness
}
