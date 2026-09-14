locals {
  backend_secrets_variable_key = "BACKEND_SECRETS"
  backend_secrets_category     = "terraform"
}

resource "tfe_variable" "production_backend_secrets" {
  workspace_id = tfe_workspace.production.id
  key          = local.backend_secrets_variable_key
  category     = local.backend_secrets_category
  hcl          = true
  sensitive    = true
  value        = jsonencode(var.PRODUCTION_BACKEND_SECRETS)
  description  = "Written into the production backend's Secrets Manager secret."
}

resource "tfe_variable" "development_pr_backend_secrets" {
  // One per open pull request, all carrying the same value: preview environments
  // are interchangeable, so there is nothing to distinguish between them.
  for_each     = tfe_workspace.development_pr
  workspace_id = each.value.id
  key          = local.backend_secrets_variable_key
  category     = local.backend_secrets_category
  hcl          = true
  sensitive    = true
  value        = jsonencode(var.DEVELOPMENT_BACKEND_SECRETS)
  description  = "Written into this pull request backend's Secrets Manager secret."
}
