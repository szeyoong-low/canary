resource "aws_iam_role" "bootstrap_role" {
  for_each = local.run_phases

  name = "${local.role_name_prefix}-${each.key}-${local.bootstrap_environment}"

  permissions_boundary = aws_iam_policy.bootstrap_boundary.arn

  tags = local.read_only_tags

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.hcp_terraform.arn
      }
      Action = local.hcp_assume_role_action
      Condition = {
        StringEquals = {
          (local.hcp_audience_claim) = local.hcp_audience
          (local.hcp_subject_claim)  = "${local.subject_organization}:${local.subject_workspace_key}:${local.bootstrap_environment}:${local.subject_run_phase_key}:${each.key}"
        }
      }
    }]
  })
}

// Non-exclusive: each of these watches one named attachment, and stays silent
// about any other policy attached to the same role. The exclusive resource
// below closes that gap.

resource "aws_iam_role_policy_attachment" "bootstrap_iam_access" {
  for_each = local.run_phases

  role       = aws_iam_role.bootstrap_role[each.key].name
  policy_arn = local.bootstrap_policy_arns[each.key]
}

// Fences the roles above: declares that the attachment declared above is the
// complete set of managed policies on each role. Nothing is attached here —
// on refresh the provider lists what is really attached, and anything absent
// from policy_arns becomes a planned detach.
//
// Read-only on the same terms as everything else in this file: iam:DetachRolePolicy
// is denied by bootstrap-boundary, so a console-added policy shows up as a diff
// that fails at apply rather than one Terraform can silently undo.
//
// Managed policies only — inline policies are fenced separately at the bottom.

resource "aws_iam_role_policy_attachments_exclusive" "bootstrap_role" {
  for_each = local.run_phases

  role_name = aws_iam_role.bootstrap_role[each.key].name

  // Read back off the attachment resource rather than the local it was built
  // from: the fence can then never disagree with what we actually declare, and
  // the reference orders the attach ahead of the fence.
  policy_arns = [aws_iam_role_policy_attachment.bootstrap_iam_access[each.key].policy_arn]
}

// The inline half of the same fence. These roles draw all their permissions from
// the managed policy attached above, so the complete set of inline policies is
// none — an empty list is the assertion, not an oversight.
//
// iam:PutRolePolicy and iam:DeleteRolePolicy are denied here too, so an inline
// policy added in the console turns the plan red and cannot be quietly deleted.

resource "aws_iam_role_policies_exclusive" "bootstrap_role" {
  for_each = local.run_phases

  role_name    = aws_iam_role.bootstrap_role[each.key].name
  policy_names = []
}
