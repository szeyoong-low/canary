// Backend

resource "aws_security_group" "alb" {
  name        = "alb-${local.name_suffix}"
  description = "Application Load Balancer for the backend."
  vpc_id      = module.vpc.vpc_id

  tags = {
    function = "network"
  }
}

resource "aws_security_group" "task" {
  name        = "task-${local.name_suffix}"
  description = "Fargate tasks running the backend container."
  vpc_id      = module.vpc.vpc_id

  tags = {
    function = "network"
  }
}

locals {
  all_ipv4      = "0.0.0.0/0"
  all_protocols = "-1" // every protocol, and so every port
  https_port    = 443
}

// Inbound

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTPS from the public Internet."

  ip_protocol = "tcp"
  from_port   = local.https_port
  to_port     = local.https_port
  cidr_ipv4   = local.all_ipv4
}

resource "aws_vpc_security_group_ingress_rule" "task_from_alb" {
  security_group_id = aws_security_group.task.id
  description       = "Container port, from the load balancer only."

  ip_protocol = "tcp"
  from_port   = local.container_port
  to_port     = local.container_port

  referenced_security_group_id = aws_security_group.alb.id
}

// Outbound - allow-all
// Default for AWS, but the Terraform provider removes it
// https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_vpc_security_group_egress_rule" "alb_all" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow all outbound from load balancer"

  ip_protocol = local.all_protocols
  cidr_ipv4   = local.all_ipv4
}

resource "aws_vpc_security_group_egress_rule" "task_all" {
  security_group_id = aws_security_group.task.id
  description       = "Allow all outbound from ECS task"

  ip_protocol = local.all_protocols
  cidr_ipv4   = local.all_ipv4
}

// Database

resource "aws_security_group" "database" {
  name        = "database-${local.name_suffix}"
  description = "PostgreSQL instance backing the backend."
  vpc_id      = module.vpc.vpc_id

  tags = {
    function = "database"
  }
}

resource "aws_vpc_security_group_ingress_rule" "database_from_task" {
  security_group_id = aws_security_group.database.id
  description       = "PostgreSQL, from the backend tasks only."

  ip_protocol = "tcp"
  from_port   = local.postgres_port
  to_port     = local.postgres_port

  referenced_security_group_id = aws_security_group.task.id
}

// There is deliberately no egress rule. A database has no reason to open a
// connection of its own, and the AWS provider strips the default allow-all.