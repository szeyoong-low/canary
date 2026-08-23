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

  // This workspace's own roles. Created in the console and adopted read-only:
  // bootstrap-boundary denies this workspace every IAM write against them.
  bootstrap_environment = "bootstrap"

  // The two run phases HCP executes. Each is both a segment of the `sub` claim
  // and the suffix distinguishing a read-only role from a writing one.
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

  // The AWS-managed policy each bootstrap role carries. A plan only ever reads,
  // so it gets no write access at all; only apply can change IAM. Both live
  // under the fixed "aws" account alias, not ours.
  // Written out rather than looked up. AWS-managed policies cannot be renamed
  // or deleted, so there is no absence for a data source to catch. Avoids a
  // paginated ListPolicies call on every plan.
  bootstrap_policy_arns = {
    (local.plan_phase)  = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
    (local.apply_phase) = "arn:aws:iam::aws:policy/IAMFullAccess"
  }
}

data "aws_caller_identity" "current" {}

// The identity provider already exists in the account and is not managed by any
// workspace, so it is read rather than created.
data "aws_iam_openid_connect_provider" "hcp_terraform" {
  url = local.hcp_oidc_provider_url
}
