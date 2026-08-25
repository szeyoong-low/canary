provider "aws" {
  region = "eu-west-2" // London

  default_tags {
    tags = {
      managed_via = "terraform"
      function    = "infrastructure-as-code"

      // The roles serving a single environment override this with their own.
      environment = "global"
    }
  }
}

locals {
  hcp_hostname          = "app.terraform.io"
  hcp_oidc_provider_url = "https://${local.hcp_hostname}"
  hcp_audience_claim    = "${local.hcp_hostname}:aud"
  hcp_subject_claim     = "${local.hcp_hostname}:sub"

  hcp_audience           = "aws.workload.identity"
  hcp_assume_role_action = "sts:AssumeRoleWithWebIdentity"
  subject_organization   = "organization:CanaryMarkets:project:Canary"

  // The claim HCP presents is a colon-delimited list of alternating keys and
  // values, in full:
  //   organization:<ORG>:project:<PROJECT>:workspace:<WORKSPACE>:run_phase:<PHASE>
  subject_workspace_key = "workspace"
  subject_run_phase_key = "run_phase"

  // Workspace names. Each doubles as the suffix on its environment's role names.
  production_environment     = "production"
  global_environment         = "global"
  development_pr_environment = "development-pr"
  bootstrap_environment      = "bootstrap"

  plan_phase  = "plan"
  apply_phase = "apply"

  run_phases = toset([local.plan_phase, local.apply_phase])

  role_name_prefix = "hcp-terraform"

  // The two permissions boundaries, adopted read-only in their own files.
  //
  // Their ARNs are assembled by hand rather than read off the resources they
  // name, because each boundary's own Deny statements refer to both boundaries
  // by ARN — including itself. A self-reference is a dependency cycle Terraform
  // refuses to build, so the ARN has to exist as a plain string first.
  workspace_boundary_name = "workspace-boundary"
  bootstrap_boundary_name = "bootstrap-boundary"
  arn_prefix              = "arn:aws:iam::"

  policy_arn_prefix = "${local.arn_prefix}${data.aws_caller_identity.current.account_id}:policy"
  role_arn_prefix   = "${local.arn_prefix}${data.aws_caller_identity.current.account_id}:role"

  workspace_boundary_arn = "${local.policy_arn_prefix}/${local.workspace_boundary_name}"
  bootstrap_boundary_arn = "${local.policy_arn_prefix}/${local.bootstrap_boundary_name}"

  // Carried by everything this workspace can read and refresh but never write.
  // Created in the console but prohibited from managing by permissions boundary.
  read_only_tags = {
    managed_via = "terraform-read-only"
  }
}

data "aws_caller_identity" "current" {}
