data "tfe_outputs" "global" {
  organization = "CanaryMarkets"
  workspace    = "global"
}

data "aws_region" "current" {}

variable "image_tag" {
  type        = string
  description = "Tag of the image in the backend repository to run: the tip commit SHA of the branch this environment tracks, under the prefix its pipeline pushed it with."

  validation {
    // The realistic failure is an empty value, which arrives when the upstream
    // build was skipped. The prefix convention belongs to the pipeline.
    condition     = length(trimspace(var.image_tag)) > 0
    error_message = "image_tag must not be empty."
  }
}

locals {
  backend_repository_url = data.tfe_outputs.global.nonsensitive_values.backend_repository_url

  container_name = "backend"

  container_port = 8000 // fastapi binds 0.0.0.0:8000 by default

  task_cpu    = 256
  task_memory = 512

  // Grace between SIGTERM and SIGKILL. A spot reclaim gives 120s and ECS spends
  // the target group's deregistration delay before this countdown even starts,
  // so the two together must fit inside that budget.
  stop_timeout         = 90
  deregistration_delay = 30

  healthcheck_interval     = 30
  healthcheck_timeout      = 5
  healthcheck_retries      = 3
  healthcheck_start_period = 60
}

resource "aws_ecs_task_definition" "backend" {
  // A family is a name whose revisions are numbered. Every apply that changes
  // anything below publishes a new revision rather than mutating this one.
  family = "backend-${local.name_suffix}"

  requires_compatibilities = ["FARGATE"]

  // The only mode Fargate supports: the task gets its own elastic network
  // interface, and so its own private address and its own security group.
  network_mode = "awsvpc"

  cpu    = local.task_cpu
  memory = local.task_memory

  execution_role_arn = aws_iam_role.task_execution.arn
  task_role_arn      = aws_iam_role.task.arn

  runtime_platform {
    // Matches the GitHub Actions runner the image is built on. Graviton would be
    // cheaper, but only once the build publishes an arm64 image.
    // Containers aren't VMs. They shares the host's kernel and runs the host's
    // CPU instructions directly. They only virtualise filesystem and namespaces.
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }

  container_definitions = jsonencode([{
    name = local.container_name

    // Immutable by tag, so this string names one exact image for the life of the
    // revision. Promotion and rollback both work by changing the tag.
    image = "${local.backend_repository_url}:${var.image_tag}"

    // The task exists to run this and nothing else, so its exit stops the task.
    essential = true

    portMappings = [{
      containerPort = local.container_port
      protocol      = "tcp"
    }]

    stopTimeout = local.stop_timeout

    // Connection details are non-sensitive as the instance is unreachable from
    // outside the VPC.
    //
    // Kept out of the backend secret deliberately. These are outputs of the
    // database resource, so sourcing them from anywhere else will lead to drift
    // (secrets must be read from somewhere with valueFrom).
    environment = [
      {
        name  = local.database_host_env
        value = local.database_host
      },
      {
        name  = local.database_port_env
        value = tostring(local.database_port)
      },
      {
        name  = local.database_name_env
        value = local.database_name
      },
      {
        name  = local.database_app_username_env
        value = local.database_app_username
      },
      {
        name  = local.database_auth_env
        value = "iam"
      },
      {
        name  = local.database_region_env
        value = data.aws_region.current.region
      },
    ]

    // Each key of the secret becomes one environment variable. The trailing
    // colons are the version stage and version id, left empty to take the
    // current version.
    // https://www.cbui.dev/how-to-get-an-aws-secrets-manager-secret-arn-by-key/
    //
    // `nonsensitive` because the keys are environment variable names, not
    // values. Without it the whole container definition would be treated as
    // sensitive and redacted from every plan.
    //
    // Resolved once, at task start. Changing a secret's value does not reach a
    // running container until the service is redeployed.
    secrets = concat(
      [
        for key in nonsensitive(keys(var.BACKEND_SECRETS)) : {
          name      = key
          valueFrom = "${aws_secretsmanager_secret.backend.arn}:${key}::"
        }
      ],
      [
        {
          name      = local.database_username_env
          valueFrom = "${local.database_secret_arn}:${local.database_username_key}::"
        },
        {
          name      = local.database_password_env
          valueFrom = "${local.database_secret_arn}:${local.database_password_key}::"
        },
      ]
    )

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = data.aws_region.current.region
        "awslogs-stream-prefix" = local.container_name
      }
    }

    // The Dockerfile must have its own healthcheck! The config here still takes precedence
    // https://docs.aws.amazon.com/AmazonECS/latest/developerguide/healthcheck.html
    healthCheck = {
      command = [
        "CMD",
        "python",
        "-c",
        "import urllib.request; urllib.request.urlopen('http://localhost:${local.container_port}/health')",
      ]

      interval    = local.healthcheck_interval
      timeout     = local.healthcheck_timeout
      retries     = local.healthcheck_retries
      startPeriod = local.healthcheck_start_period
    }
  }])

  tags = {
    function = "compute"
  }
}
