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
