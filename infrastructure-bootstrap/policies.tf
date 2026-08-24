locals {
  // The AWS-managed policy each bootstrap role carries. A plan only ever reads,
  // so it gets no write access at all; only apply can change IAM. Both live
  // under the fixed "aws" account alias, not ours.
  // Written out rather than looked up. AWS-managed policies cannot be renamed
  // or deleted, so there is no absence for a data source to catch. Avoids a
  // paginated ListPolicies call on every plan.
  bootstrap_policy_arns = {
    (local.plan_phase)  = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
    (local.apply_phase) = "arn:aws:iam::aws:policy/IAMFullAccess"
  }

  vpc_policy_arns = {
    (local.plan_phase)  = "arn:aws:iam::aws:policy/AmazonVPCReadOnlyAccess"
    (local.apply_phase) = "arn:aws:iam::aws:policy/AmazonVPCFullAccess"
  }
}