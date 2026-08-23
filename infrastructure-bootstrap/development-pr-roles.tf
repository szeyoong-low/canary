resource "aws_iam_role" "development_pr_role" {
  for_each = local.run_phases

  name = "${local.role_name_prefix}-${each.key}-${local.development_pr_environment}"

  permissions_boundary = data.aws_iam_policy.workspace_boundary.arn

  tags = {
    environment = local.development_pr_environment
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
        }
        // Wildcarded workspace segment, because every pull request gets its own
        // ephemeral workspace and their names are not known ahead of time.
        StringLike = {
          (local.hcp_subject_claim) = "${local.subject_organization}:${local.subject_workspace_key}:${local.development_pr_environment}-*:${local.subject_run_phase_key}:${each.key}"
        }
      }
    }]
  })
}