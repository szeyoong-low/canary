locals {
  // Each environment's workspace name. Only the pull request environment needs a
  // wildcard, because its workspaces are named per pull request and so cannot be
  // known ahead of time. The others contain no wildcard character, so matching
  // them with StringLike is equivalent to matching them exactly.
  workspace_environments = {
    (local.production_environment)         = local.production_environment
    (local.development_shared_environment) = local.development_shared_environment
    (local.development_pr_environment)     = "${local.development_pr_environment}-*"
  }

  // One role per environment per run phase.
  workspace_roles = {
    for pair in setproduct(keys(local.workspace_environments), tolist(local.run_phases)) :
    "${pair[0]}-${pair[1]}" => {
      environment = pair[0]
      phase       = pair[1]
      subject     = "${local.subject_organization}:${local.subject_workspace_key}:${local.workspace_environments[pair[0]]}:${local.subject_run_phase_key}:${pair[1]}"
    }
  }
}

resource "aws_iam_role" "workspace" {
  for_each = local.workspace_roles

  name = "${local.role_name_prefix}-${each.value.phase}-${each.value.environment}"

  permissions_boundary = aws_iam_policy.workspace_boundary.arn

  // Carried into the assumed session as a principal tag, which is what the
  // attribute-based access control policies will match resource tags against.
  tags = {
    environment = each.value.environment
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
        StringLike = {
          (local.hcp_subject_claim) = each.value.subject
        }
      }
    }]
  })
}
