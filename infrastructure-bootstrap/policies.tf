locals {
  // The AWS-managed policy each bootstrap role carries. A `plan` only ever reads,
  // so it gets no write access at all. Only `apply` can change IAM.
  // Written out rather than looked up. AWS-managed policies cannot be renamed
  // or deleted, so there is no absence for a data source to catch. Avoids a
  // paginated ListPolicies call on every plan.
  bootstrap_policy_arns = {
    (local.plan_phase)  = "${local.aws_managed_policy_prefix}/IAMReadOnlyAccess"
    (local.apply_phase) = "${local.aws_managed_policy_prefix}/IAMFullAccess"
  }

  vpc_policy_arns = {
    (local.plan_phase)  = "${local.aws_managed_policy_prefix}/AmazonVPCReadOnlyAccess"
    (local.apply_phase) = "${local.aws_managed_policy_prefix}/AmazonVPCFullAccess"
  }

  ecr_policy_arns = {
    (local.plan_phase)  = "${local.aws_managed_policy_prefix}/AmazonEC2ContainerRegistryReadOnly"
    (local.apply_phase) = "${local.aws_managed_policy_prefix}/AmazonEC2ContainerRegistryFullAccess"
  }
}