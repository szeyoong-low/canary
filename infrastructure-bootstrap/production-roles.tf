// These roles were created by hand in the console before this workspace
// existed, so they are adopted into state rather than created. Delete this
// block once the adopting apply has succeeded.
import {
  for_each = local.run_phases

  to = aws_iam_role.production_role[each.key]

  // aws_iam_role is imported by role name, not ARN.
  id = "${local.role_name_prefix}-${each.key}-${local.production_environment}"
}

resource "aws_iam_role" "production_role" {
  for_each = local.run_phases

  name = "${local.role_name_prefix}-${each.key}-${local.production_environment}"

  permissions_boundary = data.aws_iam_policy.workspace_boundary.arn

  tags = {
    environment = local.production_environment
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
        StringEquals = {
          (local.hcp_audience_claim) = local.hcp_audience
          (local.hcp_subject_claim)  = "${local.subject_organization}:${local.subject_workspace_key}:${local.production_environment}:${local.subject_run_phase_key}:${each.key}"
        }
      }
    }]
  })
}
