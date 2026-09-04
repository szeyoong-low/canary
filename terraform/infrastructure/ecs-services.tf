resource "aws_ecs_cluster" "backend" {
  name = "cluster-${local.name_suffix}"

  // On Fargate a cluster is just a namespace and a scheduling boundary.
  // It provisions nothing and costs nothing on its own.

  setting {
    // Costs money. Will defer until performance logging is designed properly.
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    function = "compute"
  }
}

resource "aws_ecs_cluster_capacity_providers" "backend" {
  cluster_name = aws_ecs_cluster.backend.name

  // Both are always available so a service can override the default below.
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  // Default applied to any service that does not declare a strategy of its own.

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    base              = local.is_production ? 1 : 0
    weight            = 0
  }

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }
}

locals {
  initial_task_count = 1

  // As percentage of desired_count
  // A task that is still booting is not yet healthy, so the old one has to stay.
  // Keep one task serving throughout and briefly pay for two.
  minimum_healthy_percent = 100
  maximum_percent         = 200

  // How long the load balancer's health checks are ignored after a task starts.
  // Must outlast the container's own start period, or a task is condemned for
  // failing checks it was never given time to pass.
  healthcheck_grace_period = 120
}

resource "aws_ecs_service" "backend" {
  name    = "backend-${local.name_suffix}"
  cluster = aws_ecs_cluster.backend.id

  // Names one immutable revision. Every apply that changes the task definition
  // publishes a new one and rolls the service onto it.
  task_definition = aws_ecs_task_definition.backend.arn

  desired_count = local.initial_task_count

  // Neither launch_type nor a capacity provider strategy is declared, so the
  // service inherits the cluster's default.

  network_configuration {
    subnets          = module.vpc.public_subnets
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = local.container_name
    container_port   = local.container_port
  }

  health_check_grace_period_seconds  = local.healthcheck_grace_period
  deployment_minimum_healthy_percent = local.minimum_healthy_percent
  deployment_maximum_percent         = local.maximum_percent

  deployment_circuit_breaker {
    // Stops a deployment that cannot get tasks to pass their health checks,
    // rather than retrying until the account's task launch quota is exhausted.
    enable = true

    // Redeploys the last revision known to have run. Has nothing to roll back
    // to on a brand new service, so the first deployment can only fail.
    rollback = true
  }

  // Holds the apply open until the deployment settles. Without it Terraform
  // returns as soon as ECS accepts the revision, so a crashlooping container
  // reports a green pipeline while the circuit breaker quietly reverts it.
  wait_for_steady_state = local.is_production

  force_new_deployment = true

  // Keeps tasks spread across both Availability Zones as they are replaced
  availability_zone_rebalancing = "ENABLED"

  propagate_tags = "SERVICE" // To the tasks

  tags = {
    function = "compute"
  }

  // A service cannot be created against a target group no listener forwards to.
  // The listener, because a service cannot be created against a target group
  // nothing forwards to. The sleep, so that the interfaces belonging to drained
  // tasks are released before the subnets are deleted.
  depends_on = [
    aws_lb_listener.https,
    time_sleep.eni_release,
  ]

  lifecycle {
    // Autoscaling moves this at runtime. Without the exemption every apply would
    // drag the count back to its initial value and undo whatever scaling decided.
    ignore_changes = [desired_count]
  }
}
