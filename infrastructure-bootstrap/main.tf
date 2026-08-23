provider "aws" {
  region = "eu-west-2" // London

  default_tags {
    tags = {
      managed_via = "terraform"
      function    = "infrastructure-as-code"

      // Every role below overrides this: the workspace creating a role is not
      // the environment that role serves.
      environment = terraform.workspace
    }
  }
}

locals {
  hcp_hostname          = "app.terraform.io"
  hcp_oidc_provider_url = "https://${local.hcp_hostname}"
  hcp_audience_claim    = "${local.hcp_hostname}:aud"
  hcp_subject_claim     = "${local.hcp_hostname}:sub"

  // The fixed audience HCP asks for when trading its token for AWS credentials.
  hcp_audience = "aws.workload.identity"

  // The only STS call a federated identity provider can make.
  hcp_assume_role_action = "sts:AssumeRoleWithWebIdentity"

  // Every `sub` claim HCP presents shares this prefix. Each role file appends
  // its own workspace and run phase segments.
  subject_organization = "organization:CanaryMarkets:project:Canary"

  // The claim HCP presents is a colon-delimited list of alternating keys and
  // values, in full:
  //   organization:<ORG>:project:<PROJECT>:workspace:<WORKSPACE>:run_phase:<PHASE>
  subject_workspace_key = "workspace"
  subject_run_phase_key = "run_phase"

  // Workspace names. Each doubles as the suffix on its environment's role names.
  production_environment         = "production"
  development_shared_environment = "development-shared"
  development_pr_environment     = "development-pr"

  run_phases = toset(["plan", "apply"])

  role_name_prefix = "hcp-terraform"
}

// The identity provider already exists in the account and is not managed by any
// workspace, so it is read rather than created.
data "aws_iam_openid_connect_provider" "hcp_terraform" {
  url = local.hcp_oidc_provider_url
}

// The permissions boundary capping every role this workspace creates.
// It is maintained in the console, so it is looked up by name.
data "aws_iam_policy" "workspace_boundary" {
  name = "workspace-boundary"
}