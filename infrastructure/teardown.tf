locals {
  // Long enough for AWS to reap the network interfaces the load balancer and the
  // tasks leave behind. A guess about someone else's timing, which is why the
  // teardown workflow retries rather than trusting this number.
  eni_release_delay = "300s"
}

resource "time_sleep" "eni_release" {
  // Nothing is created here and no time is spent on the way up. This resource
  // exists only to occupy a position in the destroy graph.
  destroy_duration = local.eni_release_delay

  // The problem this solves is not ordering. Terraform already tears these down
  // in the right sequence; the trouble is that DeleteLoadBalancer returns success
  // while the load balancer's interfaces are still detaching, and a drained
  // service goes INACTIVE before its tasks' interfaces are released. Terraform
  // then reaches the subnets and security groups those interfaces still reference
  // and gets DependencyViolation.
  //
  // Destroy runs in reverse dependency order, so depending on these three places
  // this sleep AFTER the load balancer and service are gone but BEFORE anything
  // still holding an interface is deleted.
  depends_on = [
    module.vpc,
    aws_security_group.alb,
    aws_security_group.task,
  ]
}
