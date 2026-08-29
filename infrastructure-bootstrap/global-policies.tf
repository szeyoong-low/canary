resource "aws_iam_role_policy_attachment" "global_ecr_access" {
  for_each = local.run_phases

  role       = aws_iam_role.workspace["${local.global_environment}-${each.key}"].name
  policy_arn = local.ecr_policy_arns[each.key]
}

resource "aws_iam_role_policy_attachments_exclusive" "global" {
  for_each = local.run_phases

  role_name   = aws_iam_role.workspace["${local.global_environment}-${each.key}"].name
  policy_arns = [aws_iam_role_policy_attachment.global_ecr_access[each.key].policy_arn]
}

resource "aws_iam_role_policies_exclusive" "global" {
  for_each = local.run_phases

  role_name    = aws_iam_role.workspace["${local.global_environment}-${each.key}"].name
  policy_names = []
}
