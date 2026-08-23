// These roles were created by hand in the console before this workspace
// existed, so they are adopted into state rather than created. Delete this
// block once the adopting apply has succeeded.
import {
  for_each = local.run_phases

  to = aws_iam_role.development_shared_role[each.key]

  // aws_iam_role is imported by role name, not ARN.
  id = "${local.role_name_prefix}-${each.key}-${local.development_shared_environment}"
}

resource "aws_iam_role" "development_shared_role" {
  for_each = local.run_phases

  name = "${local.role_name_prefix}-${each.key}-${local.development_shared_environment}"

  permissions_boundary = data.aws_iam_policy.workspace_boundary.arn

  tags = {
    environment = local.development_shared_environment
  }

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = data.aws_iam_openid_connect_provider.hcp_terraform.arn
      }
      Action = local.hcp_assume_role_action
      Condition = {
        // Exact match, so the ephemeral pull request workspaces cannot assume the
        // role that owns resources shared across all development environments.
        StringEquals = {
          (local.hcp_audience_claim) = local.hcp_audience
          (local.hcp_subject_claim)  = "${local.subject_organization}:${local.subject_workspace_key}:${local.development_shared_environment}:${local.subject_run_phase_key}:${each.key}"
        }
      }
    }]
  })
}
