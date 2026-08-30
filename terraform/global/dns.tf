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

  // DNS records managed by infrastructure workspaces. Passed to them as an output
  backend_hostname = "api.canary.markets"
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
