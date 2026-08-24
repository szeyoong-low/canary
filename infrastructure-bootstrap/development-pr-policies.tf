resource "aws_iam_role_policy_attachment" "development_pr_vpc_access" {
  for_each = local.run_phases

  role       = aws_iam_role.workspace["${local.development_pr_environment}-${each.key}"].name
  policy_arn = local.vpc_policy_arns[each.key]
}

resource "aws_iam_role_policy_attachments_exclusive" "development_pr" {
  for_each = local.run_phases

  role_name   = aws_iam_role.workspace["${local.development_pr_environment}-${each.key}"].name
  policy_arns = [aws_iam_role_policy_attachment.development_pr_vpc_access[each.key].policy_arn]
}

resource "aws_iam_role_policies_exclusive" "development_pr" {
  for_each = local.run_phases

  role_name    = aws_iam_role.workspace["${local.development_pr_environment}-${each.key}"].name
  policy_names = []
}
