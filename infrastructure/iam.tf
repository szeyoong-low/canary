data "aws_caller_identity" "current" {}

data "tfe_outputs" "bootstrap" {
  organization = "CanaryMarkets"
  workspace    = "bootstrap"
}

locals {
  aws_managed_policy_prefix = "arn:aws:iam::aws:policy"

  workspace_boundary_arn = data.tfe_outputs.bootstrap.nonsensitive_values.workspace_boundary_arn

  // Both roles are handed to ECS, which assumes them on this account's behalf.
  ecs_tasks_service_principal = "ecs-tasks.amazonaws.com"

  ecs_assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = local.ecs_tasks_service_principal }
      Action    = "sts:AssumeRole"

      // Guards against the confused deputy: ECS may only assume these roles
      // while acting for this account, not while acting for someone else's.
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

// Assumed by the ECS agent, not by the application. Everything it does happens
// before and around the container, never inside it.
resource "aws_iam_role" "task_execution" {
  name        = "ecs-task-execution-${local.name_suffix}"
  description = "Lets the ECS agent pull the backend image and write its logs."

  assume_role_policy = local.ecs_assume_role_policy

  // Required twice over by the workspace boundary: once because CreateRole is
  // denied without it, and again because PassRole to ECS is denied for any role
  // that lacks it.
  permissions_boundary = local.workspace_boundary_arn

  tags = {
    function = "compute"
  }
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "${local.aws_managed_policy_prefix}/service-role/AmazonECSTaskExecutionRolePolicy"
}

// Assumed by the application itself
resource "aws_iam_role" "task" {
  name        = "ecs-task-assumed-${local.name_suffix}"
  description = "The identity the backend container assumes when running"

  assume_role_policy   = local.ecs_assume_role_policy
  permissions_boundary = local.workspace_boundary_arn

  tags = {
    function = "compute"
  }
}
