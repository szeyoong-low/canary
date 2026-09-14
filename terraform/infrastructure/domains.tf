locals {
  pull_request_number = trimprefix(local.workspace, "${local.development_pr_prefix}-")

  api_subdomain = data.tfe_outputs.global.nonsensitive_values.backend_hostname

  backend_hostname = (
    local.is_production
    ? local.api_subdomain
    : "dev-${local.pull_request_number}-${local.api_subdomain}"
  )
}

resource "cloudflare_dns_record" "backend" {
  zone_id = data.tfe_outputs.global.nonsensitive_values.cloudflare_zone_id

  name = local.backend_hostname
  type = "CNAME"

  // A load balancer has no stable address, so it is always named rather than
  // pointed at. AWS moves the addresses behind this name as it scales.
  content = aws_lb.backend.dns_name

  proxied = true
  ttl     = 1 // Automatic, required when proxied
}
