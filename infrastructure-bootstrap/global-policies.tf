resource "aws_iam_role_policy_attachment" "global" {
  for_each = local.global_policies

  role       = aws_iam_role.workspace["${local.global_environment}-${each.value.phase}"].name
  policy_arn = each.value.arn
}

resource "aws_iam_role_policy_attachments_exclusive" "global" {
  for_each = local.run_phases

  role_name   = aws_iam_role.workspace["${local.global_environment}-${each.key}"].name
  policy_arns = [for policy in local.global_policies : policy.arn if policy.phase == each.key]
}

resource "aws_iam_role_policies_exclusive" "global" {
  for_each = local.run_phases

  role_name    = aws_iam_role.workspace["${local.global_environment}-${each.key}"].name
  policy_names = []
}
