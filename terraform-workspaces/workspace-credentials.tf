locals {
  aws_credential_constants = {
    TFC_AWS_PROVIDER_AUTH              = "true"
    TFC_AWS_WORKLOAD_IDENTITY_AUDIENCE = "aws.workload.identity"
  }

  // `nonsensitive_values`, not `values`: the latter marks every output sensitive,
  // and Terraform refuses to iterate over a sensitive value.
  //
  // Bootstrap is deliberately absent. It holds the roles everything else depends
  // on, so its own credentials stay console-owned — if this configuration wrote a
  // bad ARN there, layer 0 could no longer authenticate to repair itself.
  workspace_aws_credentials = {
    (local.production_environment)     = data.tfe_outputs.bootstrap.nonsensitive_values.production_oidc_roles
    (local.global_environment)         = data.tfe_outputs.bootstrap.nonsensitive_values.global_oidc_roles
    (local.development_pr_environment) = data.tfe_outputs.bootstrap.nonsensitive_values.development_pr_oidc_roles
  }

  workspace_aws_credential_variables = merge([
    for environment, roles in local.workspace_aws_credentials : {
      for key, value in merge(local.aws_credential_constants, roles) :
      "${environment}/${key}" => {
        environment = environment
        key         = key
        value       = value
      }
    }
  ]...)
}

resource "tfe_variable_set" "aws_credentials" {
  for_each = local.workspace_aws_credentials

  name        = "${each.key}-aws-credentials"
  description = "Dynamic AWS credentials for the ${each.key} environment."
}

resource "tfe_variable" "aws_credentials" {
  for_each = local.workspace_aws_credential_variables

  key             = each.value.key
  value           = each.value.value
  category        = "env" // HCP injects these into the run environment, not into Terraform.
  variable_set_id = tfe_variable_set.aws_credentials[each.value.environment].id
}

resource "tfe_workspace_variable_set" "production" {
  workspace_id    = tfe_workspace.production.id
  variable_set_id = tfe_variable_set.aws_credentials[local.production_environment].id
}

resource "tfe_workspace_variable_set" "global" {
  workspace_id    = tfe_workspace.global.id
  variable_set_id = tfe_variable_set.aws_credentials[local.global_environment].id
}

resource "tfe_workspace_variable_set" "development_pr" {
  for_each = tfe_workspace.development_pr

  workspace_id    = each.value.id
  variable_set_id = tfe_variable_set.aws_credentials[local.development_pr_environment].id
}
