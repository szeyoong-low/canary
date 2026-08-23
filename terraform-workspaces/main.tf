// Authenticated by a Terraform team token set on this workspace.
provider "tfe" {
  organization = "CanaryMarkets"
}

data "tfe_project" "canary" {
  name = "Canary"
}

locals {
  // Workspace names, which double as environment names throughout.
  // Named to match the identical locals in infrastructure-bootstrap.
  production_environment         = "production"
  development_shared_environment = "development-shared"
  development_pr_environment     = "development-pr"
  bootstrap_environment          = "bootstrap"
}

data "tfe_outputs" "bootstrap" {
  workspace = local.bootstrap_environment
}
