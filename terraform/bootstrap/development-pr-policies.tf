resource "aws_iam_role_policy_attachment" "development_pr" {
  for_each = local.prod_dev_shared_policies

  role       = aws_iam_role.workspace["${local.development_pr_environment}-${each.value.phase}"].name
  policy_arn = each.value.arn
}

resource "aws_iam_role_policy_attachments_exclusive" "development_pr" {
  for_each = local.run_phases

  role_name   = aws_iam_role.workspace["${local.development_pr_environment}-${each.key}"].name
  policy_arns = [for policy in local.prod_dev_shared_policies : policy.arn if policy.phase == each.key]
}

resource "aws_iam_role_policies_exclusive" "development_pr" {
  for_each = local.run_phases

  role_name    = aws_iam_role.workspace["${local.development_pr_environment}-${each.key}"].name
  policy_names = []
}
