locals {
  pull_request_number = trimprefix(local.workspace, "${local.development_pr_prefix}-")

  // The frontend Worker derives this same hostname from its own preview URL, so
  // the two mappings have to agree exactly.
  api_subdomain = "api.canary.markets"

  backend_hostname = (
    local.is_production
    ? local.api_subdomain
    : "dev-${local.pull_request_number}-${local.api_subdomain}"
  )
}

resource "cloudflare_dns_record" "backend" {
  // Production's hostname is still the Railway record owned by the global
  // workspace, and Cloudflare will not hold two records for one name.
  // An empty set builds nothing, a single-element one builds the record. Keyed by
  // the hostname rather than a position, so the address in state reads as
  // backend["dev-3-api.canary.markets"] and says which name it holds.
  for_each = local.is_production ? toset([]) : toset([local.backend_hostname])

  zone_id = data.tfe_outputs.global.nonsensitive_values.cloudflare_zone_id

  name = each.value
  type = "CNAME"

  // A load balancer has no stable address, so it is always named rather than
  // pointed at. AWS moves the addresses behind this name as it scales.
  content = aws_lb.backend.dns_name

  proxied = true
  ttl     = 1 // Automatic, required when proxied
}
