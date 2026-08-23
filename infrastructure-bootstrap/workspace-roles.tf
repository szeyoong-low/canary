locals {
  // Each environment's workspace name, and the IAM condition operator that matches
  // it. Only the pull request environment needs a wildcard, because its workspaces
  // are named per pull request and so cannot be known ahead of time.
  workspace_environments = {
    (local.production_environment) = {
      workspace_pattern = local.production_environment
      subject_operator  = "StringEquals"
    }
    (local.development_shared_environment) = {
      workspace_pattern = local.development_shared_environment
      subject_operator  = "StringEquals"
    }
    (local.development_pr_environment) = {
      workspace_pattern = "${local.development_pr_environment}-*"
      subject_operator  = "StringLike"
    }
  }

  // One role per environment per run phase.
  workspace_roles = {
    for pair in setproduct(keys(local.workspace_environments), tolist(local.run_phases)) :
    "${pair[0]}-${pair[1]}" => {
      environment      = pair[0]
      phase            = pair[1]
      subject_operator = local.workspace_environments[pair[0]].subject_operator
      subject          = "${local.subject_organization}:${local.subject_workspace_key}:${local.workspace_environments[pair[0]].workspace_pattern}:${local.subject_run_phase_key}:${pair[1]}"
    }
  }
}

resource "aws_iam_role" "workspace" {
  for_each = local.workspace_roles

  name = "${local.role_name_prefix}-${each.value.phase}-${each.value.environment}"

  permissions_boundary = data.aws_iam_policy.workspace_boundary.arn

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

      // The audience is always matched exactly, so StringEquals is always present.
      // The subject joins it there for the exactly named workspaces, or lands in a
      // StringLike block of its own for the wildcarded pull request workspaces.
      // The unused operator is dropped entirely rather than left as an empty
      // object, which AWS would reject.
      Condition = {
        for operator, claims in {
          StringEquals = merge(
            { (local.hcp_audience_claim) = local.hcp_audience },
            each.value.subject_operator == "StringEquals" ? { (local.hcp_subject_claim) = each.value.subject } : {}
          )
          StringLike = each.value.subject_operator == "StringLike" ? { (local.hcp_subject_claim) = each.value.subject } : {}
        } : operator => claims if length(claims) > 0
      }
    }]
  })
}

// The roles below were already applied under one resource block per environment.
// These blocks tell Terraform the existing state entries belong to the collapsed
// resource, so the plan reports moves instead of destroying and recreating six
// live roles. Safe to delete once the move has been applied.
moved {
  from = aws_iam_role.production_role["plan"]
  to   = aws_iam_role.workspace["production-plan"]
}

moved {
  from = aws_iam_role.production_role["apply"]
  to   = aws_iam_role.workspace["production-apply"]
}

moved {
  from = aws_iam_role.development_shared_role["plan"]
  to   = aws_iam_role.workspace["development-shared-plan"]
}

moved {
  from = aws_iam_role.development_shared_role["apply"]
  to   = aws_iam_role.workspace["development-shared-apply"]
}

moved {
  from = aws_iam_role.development_pr_role["plan"]
  to   = aws_iam_role.workspace["development-pr-plan"]
}

moved {
  from = aws_iam_role.development_pr_role["apply"]
  to   = aws_iam_role.workspace["development-pr-apply"]
}
