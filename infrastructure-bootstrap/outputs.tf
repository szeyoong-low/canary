output "production_oidc_roles" {
  description = "HCP environment variables that grant the production workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.production_environment}-plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.production_environment}-apply"].arn
  }
}

output "development_shared_oidc_roles" {
  description = "HCP environment variables that grant the shared development workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.development_shared_environment}-plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.development_shared_environment}-apply"].arn
  }
}

output "development_pr_oidc_roles" {
  description = "HCP environment variables that grant a pull request workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.workspace["${local.development_pr_environment}-plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.workspace["${local.development_pr_environment}-apply"].arn
  }
}
