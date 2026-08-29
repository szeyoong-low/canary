// Backend

resource "cloudflare_dns_record" "api" {
  zone_id = local.cloudflare_zone_id
  name    = "api.canary.markets"
  type    = "CNAME"
  content = "88ffa0vh.up.railway.app"
  proxied = true
  ttl     = 1
}

resource "cloudflare_dns_record" "www_api" {
  zone_id = local.cloudflare_zone_id
  name    = "www.api.canary.markets"
  type    = "CNAME"
  content = "nhtnxlax.up.railway.app"
  proxied = true
  ttl     = 1
}

// Ownership proofs Railway issues per custom domain.
resource "cloudflare_dns_record" "railway_verify_api" {
  zone_id = local.cloudflare_zone_id
  name    = "_railway-verify.api.canary.markets"
  type    = "TXT"
  content = "\"railway-verify=2b4f4a7e5f69469049de11706ffd2b41f94fb20ef8da198a26b5f8560bf00d6c\""
  ttl     = 3600
}

resource "cloudflare_dns_record" "railway_verify_www_api" {
  zone_id = local.cloudflare_zone_id
  name    = "_railway-verify.www.api.canary.markets"
  type    = "TXT"
  content = "\"railway-verify=69c9824a0f2957215bc08cd5c2be30a538aa5c9bc6211f0c416c2ef60eebc973\""
  ttl     = 1
}

// Mail

locals {
  // Namecheap's email-forwarding servers
  mx_records = {
    "eforward1.registrar-servers.com" = 10
    "eforward2.registrar-servers.com" = 10
    "eforward3.registrar-servers.com" = 10
    "eforward4.registrar-servers.com" = 15
    "eforward5.registrar-servers.com" = 20
  }
}

resource "cloudflare_dns_record" "mx" {
  for_each = local.mx_records

  zone_id  = local.cloudflare_zone_id
  name     = "canary.markets"
  type     = "MX"
  content  = each.key
  priority = each.value
  ttl      = 1
}

// Unclassified

resource "cloudflare_dns_record" "mailboxes_www" {
  for_each = toset(["64.29.17.1", "64.29.17.65"])

  zone_id = local.cloudflare_zone_id
  name    = "www.mailboxes.canary.markets"
  type    = "A"
  content = each.key
  proxied = true
  ttl     = 1
}
