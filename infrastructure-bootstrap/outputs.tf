output "production_oidc_roles" {
  description = "HCP environment variables that grant the production workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.production_role["plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.production_role["apply"].arn
  }
}

output "development_shared_oidc_roles" {
  description = "HCP environment variables that grant the shared development workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.development_shared_role["plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.development_shared_role["apply"].arn
  }
}

output "development_pr_oidc_roles" {
  description = "HCP environment variables that grant a pull request workspace dynamic AWS credentials."

  value = {
    TFC_AWS_PLAN_ROLE_ARN  = aws_iam_role.development_pr_role["plan"].arn
    TFC_AWS_APPLY_ROLE_ARN = aws_iam_role.development_pr_role["apply"].arn
  }
}
