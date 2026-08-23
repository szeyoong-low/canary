resource "tfe_workspace" "development_pr" {
  for_each = var.pull_request_numbers

  name       = "${local.development_pr_environment}-${each.value}"
  project_id = data.tfe_project.canary.id

  // The deploy workflow creates a run and confirms it explicitly, so HCP must not
  // apply on its own.
  auto_apply = false

  force_delete = false

  allow_destroy_plan = true
}
