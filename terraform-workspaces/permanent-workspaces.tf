// Self-managing is not possible as a Terraform configuration cannot create the
// workspace it is running in.

resource "tfe_workspace" "production" {
  name        = local.production_environment
  project_id  = data.tfe_project.canary.id
  description = "Production infrastructure. Run from CI/CD pipeline."

  // The deploy workflow creates a run and confirms it explicitly, so HCP must not
  // apply on its own. Merging the pull request is what signs off the plan.
  auto_apply = false

  force_delete = false

  // prevent_destroy stops Terraform deleting this workspace object.
  // this stops anyone from destroying the infrastructure inside it.
  allow_destroy_plan = false

  lifecycle {
    prevent_destroy = true
  }
}

// One-shot import of the pre-existing workspace, created by hand before this
// configuration managed it. Remove once the apply has run.
import {
  to = tfe_workspace.global
  id = "CanaryMarkets/${local.global_environment}"
}

resource "tfe_workspace" "global" {
  name        = local.global_environment
  project_id  = data.tfe_project.canary.id
  description = "Long-lived resources shared by every ephemeral development environment. Run from CI/CD pipeline."

  auto_apply = false

  force_delete = false

  allow_destroy_plan = false

  lifecycle {
    prevent_destroy = true
  }
}

resource "tfe_workspace" "bootstrap" {
  name        = local.bootstrap_environment
  project_id  = data.tfe_project.canary.id
  description = "The OIDC provider and IAM roles every other workspace authenticates with. Run from the CLI."

  auto_apply = false

  force_delete = false

  allow_destroy_plan = false

  lifecycle {
    prevent_destroy = true
  }
}