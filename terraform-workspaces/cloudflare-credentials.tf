variable "CLOUDFLARE_API_TOKEN" {
  type        = string
  description = "Cloudflare API token with DNS edit rights on the canary.markets zone. Every workspace that writes a DNS record authenticates with this."
  sensitive   = true
}

locals {
  cloudflare_credential_key = "CLOUDFLARE_API_TOKEN"
  cloudflare_credential_category = "env"
}

resource "tfe_variable" "global_cloudflare_api_token" {
  workspace_id = tfe_workspace.global.id
  key          = local.cloudflare_credential_key
  category     = local.cloudflare_credential_category
  sensitive    = true
  value        = var.CLOUDFLARE_API_TOKEN
  description  = "Read by the Cloudflare provider managing the zone's long-lived records."
}

resource "tfe_variable" "production_cloudflare_api_token" {
  workspace_id = tfe_workspace.production.id
  key          = local.cloudflare_credential_key
  category     = local.cloudflare_credential_category
  sensitive    = true
  value        = var.CLOUDFLARE_API_TOKEN
  description  = "Read by the Cloudflare provider managing the production backend's record."
}

resource "tfe_variable" "development_pr_cloudflare_api_token" {
  // One per open pull request, all carrying the same value. Cloudflare tokens are
  // scoped to a zone, and every environment writes into the same one.
  for_each     = tfe_workspace.development_pr
  workspace_id = each.value.id
  key          = local.cloudflare_credential_key
  category     = local.cloudflare_credential_category
  sensitive    = true
  value        = var.CLOUDFLARE_API_TOKEN
  description  = "Read by the Cloudflare provider managing this pull request backend's record."
}
