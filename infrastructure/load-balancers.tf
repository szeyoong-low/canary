locals {
  // Distinct from the task definition's healthCheck, which notices a wedged
  // container and replaces it. This one only decides where to route.
  target_healthcheck_path      = "/health"
  target_healthcheck_interval  = 30
  target_healthcheck_timeout   = 5
  target_healthy_threshold     = 2
  target_unhealthy_threshold   = 3
  target_healthcheck_successes = "200"

  // A per-connection inactivity timer. Raised above the 60s default because the
  // agent can spend longer than that waiting on an inference provider before it
  // emits its first byte, and the load balancer would otherwise return a 504
  // Bad Gateway.
  alb_idle_timeout = 120

  // Cut once, TLS 1.2 and above. Anything older is a liability and no browser
  // this app serves needs it.
  alb_ssl_policy = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

resource "aws_lb" "backend" {
  name               = "alb-${local.name_suffix}"
  load_balancer_type = "application"
  internal           = false

  // One subnet per Availability Zone. The load balancer places a node in each
  // and is the reason two zones are mandatory.
  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.alb.id]

  idle_timeout = local.alb_idle_timeout

  // Rejects rather than forwards headers that do not parse. Without it a
  // malformed header can be read differently by the load balancer and by
  // uvicorn, which is the shape of a request smuggling exploint.
  drop_invalid_header_fields = true

  // Production refuses to be deleted; pull request environments are torn down on
  // every close and must not.
  enable_deletion_protection = local.is_production

  tags = {
    function = "network"
  }
}

resource "aws_lb_target_group" "backend" {
  name = "target-${local.name_suffix}"

  // Required by awsvpc networking: a Fargate task has its own elastic network
  // interface and is registered by address, as there is no instance to name.
  target_type = "ip"

  port     = local.container_port
  protocol = "HTTP" // Already inside the VPC, past TLS termination
  vpc_id   = module.vpc.vpc_id

  // How long the load balancer keeps forwarding in-flight requests to a task it
  // has stopped sending new ones to.
  deregistration_delay = local.deregistration_delay

  health_check {
    path     = local.target_healthcheck_path
    protocol = "HTTP"
    matcher  = local.target_healthcheck_successes
    interval = local.target_healthcheck_interval
    timeout  = local.target_healthcheck_timeout

    // Deliberately asymmetric: two passes to start receiving traffic, three
    // failures to stop. Quick to trust a new task, slow to condemn a live one
    // over a blip.
    healthy_threshold   = local.target_healthy_threshold
    unhealthy_threshold = local.target_unhealthy_threshold
  }

  lifecycle {
    // A target group cannot be deleted while a listener forwards to it, so any
    // change forcing replacement deadlocks unless the new one is made first.
    create_before_destroy = true
  }

  tags = {
    function = "network"
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.backend.arn

  port     = local.https_port
  protocol = "HTTPS"

  ssl_policy      = local.alb_ssl_policy
  certificate_arn = data.tfe_outputs.global.nonsensitive_values.api_tls_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }

  tags = {
    function = "network"
  }
}
