output "production_oidc_roles" {
  description = "HCP environment variables that grant the production workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.production_environment}-${local.plan_phase}"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.production_environment}-${local.apply_phase}"].arn
  }
}

output "global_oidc_roles" {
  description = "HCP environment variables that grant the shared development workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.global_environment}-${local.plan_phase}"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.global_environment}-${local.apply_phase}"].arn
  }
}

output "development_pr_oidc_roles" {
  description = "HCP environment variables that grant a pull request workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.development_pr_environment}-${local.plan_phase}"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.development_pr_environment}-${local.apply_phase}"].arn
  }
}

output "github_actions_oidc_roles" {
  description = "GitHub Actions repository variables holding roles that manage push and promote artifacts."

  value = {
    AWS_ECR_ROLE_ARN = aws_iam_role.github_actions_ecr.arn
  }
}

output "workspace_boundary_arn" {
  description = "Permissions boundary every role an environment workspace creates must carry, for those workspaces to attach to their own roles."
  value = aws_iam_policy.workspace_boundary.arn
}
