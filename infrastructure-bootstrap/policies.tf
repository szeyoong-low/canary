locals {
  customer_managed_policy_name_prefix = "canary-"

  // The AWS-managed policy each bootstrap role carries. A `plan` only ever reads,
  // so it gets no write access at all. Only `apply` can change IAM.
  //
  // Written out rather than looked up. AWS-managed policies cannot be renamed
  // or deleted, so there is no absence for a data source to catch. Avoids a
  // paginated ListPolicies call on every plan.
  bootstrap_policy_arns = {
    (local.plan_phase)  = "${local.aws_managed_policy_prefix}/IAMReadOnlyAccess"
    (local.apply_phase) = "${local.aws_managed_policy_prefix}/IAMFullAccess"
  }

  // The policies the global workspace carries, one family per service.
  global_policy_families = {
    // Repository, lifecycle policy, scanning configuration
    ecr = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/AmazonEC2ContainerRegistryReadOnly"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/AmazonEC2ContainerRegistryFullAccess"
    }

    // TLS certificates and their DNS validation
    acm = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/AWSCertificateManagerReadOnly"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/AWSCertificateManagerFullAccess"
    }
  }

  // Flattened the same way as the prod/dev families below.
  global_policies = merge([
    for phase in local.run_phases : {
      for family, arns in local.global_policy_families :
      "${phase}-${family}" => {
        phase = phase
        arn   = arns[phase]
      }
    }
  ]...)

  // The policies production and development workspaces carry, one family per service.
  prod_dev_shared_policy_families = {
    // Subnets, route tables, internet gateway, security groups
    vpc = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/AmazonVPCReadOnlyAccess"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/AmazonVPCFullAccess"
    }

    // Clusters, task definitions, services. AWS publishes no read-only managed
    // policy for ECS.
    ecs = {
      (local.plan_phase)  = aws_iam_policy.ecs_read_only.arn
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/AmazonECS_FullAccess"
    }

    // Task roles and execution roles (this and roles created are capped by workspace boundary)
    iam = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/IAMReadOnlyAccess"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/IAMFullAccess"
    }

    // Log groups
    logs = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/CloudWatchLogsReadOnlyAccess"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/CloudWatchLogsFullAccess"
    }

    // The plan phase can read secret material, unavoidably: Terraform refreshes
    // aws_secretsmanager_secret_version by calling GetSecretValue, so a plan role
    // that cannot read the values cannot refresh the resource at all.
    //
    // AWSSecretsManagerClientReadOnlyAccess is written for the client case, an
    // application fetching a value at runtime, and omits the reads that managing
    // a secret's configuration needs. Hence the hand-rolled policy below.
    secretsmanager = {
      (local.plan_phase)  = aws_iam_policy.secretsmanager_read_only.arn
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/SecretsManagerReadWrite"
    }

    // Load balancer, target groups
    elb = {
      (local.plan_phase)  = "${local.aws_managed_policy_prefix}/ElasticLoadBalancingReadOnly"
      (local.apply_phase) = "${local.aws_managed_policy_prefix}/ElasticLoadBalancingFullAccess"
    }
  }

  // Flattened to "<phase>-<family>" => { phase, arn } so a single `for_each` can
  // drive every attachment.
  prod_dev_shared_policies = merge([
    for phase in local.run_phases : {
      for family, arns in local.prod_dev_shared_policy_families :
      "${phase}-${family}" => {
        phase = phase
        arn   = arns[phase]
      }
    }
  ]...)
}

resource "aws_iam_policy" "ecs_read_only" {
  name        = "${local.customer_managed_policy_name_prefix}ecs-read-only"
  description = "Refresh and plan ECS resources without being able to change them."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"

      Action = [
        "ecs:Describe*",
        "ecs:List*",
      ]

      // Most ECS List* actions take no resource ARN, so a scoped Resource would
      // deny them outright. Environment isolation comes from the principal tags
      // and the permissions boundary, not from here.
      Resource = "*"
    }]
  })
}

// The plan-phase counterpart to SecretsManagerReadWrite. Every action here is one
// the AWS provider issues while refreshing the two secret resources.
resource "aws_iam_policy" "secretsmanager_read_only" {
  name        = "${local.customer_managed_policy_name_prefix}secretsmanager-read-only"
  description = "Refresh and plan Secrets Manager resources without being able to change them."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"

      // Enumerated rather than matched by verb, unlike the ECS policy above.
      // secretsmanager:Get* would also cover GetSecretValue, and a role that can
      // read secret material should say so outright rather than acquire it as a
      // side effect of a wildcard.
      Action = [
        // The secret's own configuration.
        "secretsmanager:DescribeSecret",

        // Populates the `policy` attribute, which is the resource-based policy.
        // Read on every plan even though none is set.
        "secretsmanager:GetResourcePolicy",

        // The two below refresh aws_secretsmanager_secret_version, which cannot
        // be read without reading the material it holds.
        "secretsmanager:ListSecretVersionIds",
        "secretsmanager:GetSecretValue",
      ]

      Resource = "*"
    }]
  })
}
