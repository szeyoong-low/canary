locals {
  api_subdomain          = "api.canary.markets"
  api_wildcard_subdomain = "*.${local.api_subdomain}" // One label deep: covers www.api & dev-n.api
}

resource "aws_acm_certificate" "api" {
  // Regional, so it must sit in the same region as the load
  // balancers that reference it.

  domain_name               = local.api_subdomain
  subject_alternative_names = [local.api_wildcard_subdomain]

  validation_method = "DNS" // Implemented below

  tags = {
    function = "network"
  }

  lifecycle {
    // A certificate a listener is using cannot be deleted. Without this, editing
    // the names above would deadlock: the replacement cannot be created under
    // the same identity until the original is destroyed, and it cannot be.
    create_before_destroy = true
  }
}

resource "cloudflare_dns_record" "api_certificate_validation" {
  // A CA won't issue a certificate for a name you haven't proven you control
  // ACM generates a random token, tells you to publish it at a specific
  // _-prefixed name in the DNS, then looks it up.

  // ACM collapses the apex and its wildcard onto a single validation CNAME record,
  // so drop the wildcard or the same record gets written twice and collides.
  //
  // Keyed on domain_name because for_each keys must be known while the plan is
  // built, before ACM has been called. domain_name is echoed back from the
  // arguments above; resource_record_name is invented by ACM at create time.
  for_each = {
    for dvo in aws_acm_certificate.api.domain_validation_options :
    dvo.domain_name => dvo
    if dvo.domain_name != local.api_wildcard_subdomain
  }

  zone_id = local.cloudflare_zone_id

  // Trailing dots are how ACM writes a fully qualified name. Cloudflare wants
  // them without.
  name    = trimsuffix(each.value.resource_record_name, ".")
  type    = each.value.resource_record_type
  content = trimsuffix(each.value.resource_record_value, ".")

  // Proxying means Cloudflare stops publishing your record's real value.
  // Instead it answers public DNS queries with Cloudflare's own anycast IP
  // addresses, so traffic hits their edge first.
  proxied = false

  ttl = 60 // Short cache, because the record is only read during issuance and renewal
}

resource "aws_acm_certificate_validation" "api" {
  certificate_arn = aws_acm_certificate.api.arn

  // Blocks the apply until ACM reports ISSUED. This resource creates nothing.
  validation_record_fqdns = [
    for record in cloudflare_dns_record.api_certificate_validation : record.name
  ]
}
