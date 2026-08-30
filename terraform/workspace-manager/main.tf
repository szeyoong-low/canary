// Authenticated by a Terraform team token set on this workspace.
provider "tfe" {
  organization = "CanaryMarkets"
}

data "tfe_project" "canary" {
  name = "Canary"
}

locals {
  // Workspace names, which double as environment names throughout.
  // Named to match the identical locals in terraform/bootstrap.
  production_environment     = "production"
  global_environment         = "global"
  development_pr_environment = "development-pr"
  bootstrap_environment      = "bootstrap"
}

data "tfe_outputs" "bootstrap" {
  workspace = local.bootstrap_environment
}
