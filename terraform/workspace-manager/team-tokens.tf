// A token that lets the infrastructure workspaces read the workspace outputs.

// The owners team, because the free plan has no team management.
// Team tokens cannot be scoped, so it carries org-wide read and write permissions.
data "tfe_team" "owners" {
  name = "owners"
}

resource "tfe_team_token" "output_reader" {
  team_id = data.tfe_team.owners.id

  // Load-bearing. Descriptions must be unique per team, so a token created
  // without a description replaces the team's legacy token, which is the one
  // created in the console for this very workspace to authenticate with 
  description = "Lets the production and development workspaces read workspace outputs."

  // HCP's default
  expired_at = "2028-08-29T00:00:00Z"
}

resource "tfe_variable_set" "output_read" {
  name        = "output-read-credentials"
  description = "Token for reading the global workspace's outputs via the tfe provider."
}

resource "tfe_variable" "output_read_token" {
  key             = "TFE_TOKEN"
  value           = tfe_team_token.output_reader.token
  category        = "env" // The tfe provider reads this from the run environment.
  sensitive       = true
  variable_set_id = tfe_variable_set.output_read.id
}

resource "tfe_workspace_variable_set" "production_output_read" {
  workspace_id    = tfe_workspace.production.id
  variable_set_id = tfe_variable_set.output_read.id
}

resource "tfe_workspace_variable_set" "development_pr_output_read" {
  for_each = tfe_workspace.development_pr

  workspace_id    = each.value.id
  variable_set_id = tfe_variable_set.output_read.id
}
