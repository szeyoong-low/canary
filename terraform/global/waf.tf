locals {
  health_check_user_agent = "canary-health-check/1"

  backend_hostname = "api.canary.markets"

  // Every pull request raises an ephemeral backend at `dev-<number>-` prefixed
  // onto the production name, so the set cannot be enumerated here and is
  // matched by shape instead. See `backend_hostname` in
  // terraform/infrastructure/dns.tf, which builds the name this must mirror.
  //
  // The two ends are both anchored, so this describes exactly that shape and
  // not merely a name containing it. Any host under this zone is one we
  // created, so the wildcard grants nothing an attacker can register into.
  development_backend_hostnames = join(" and ", [
    "starts_with(http.host, \"dev-\")",
    "ends_with(http.host, \"-${local.backend_hostname}\")",
  ])

  frontend_hostnames = [
    cloudflare_workers_custom_domain.apex.hostname,
    cloudflare_workers_custom_domain.www.hostname,
  ]
}

// A zone may hold only one entrypoint ruleset per phase, so this resource owns
// *every* custom WAF rule on the zone.
resource "cloudflare_ruleset" "zone_custom_firewall" {
  zone_id     = local.cloudflare_zone_id
  name        = "Custom firewall rules"
  kind        = "zone"
  phase       = "http_request_firewall_custom"
  description = "Managed in terraform/global/waf.tf"

  rules = [{
    description = "Allow deployment health checks past bot mitigation"
    enabled     = true
    action      = "skip"

    expression = join(" and ", [
      "(${join(" or ", [
        "(http.host in {${join(" ", formatlist("\"%s\"", local.frontend_hostnames))}} and http.request.uri.path eq \"/\")",
        "((http.host eq \"${local.backend_hostname}\" or (${local.development_backend_hostnames})) and http.request.uri.path eq \"/health\")",
      ])})",
      "(http.request.method eq \"GET\")",
      "(http.request.uri.query eq \"\")",
      "(http.user_agent eq \"${local.health_check_user_agent}\")",
    ])

    action_parameters = {
      // Stop evaluating the rest of this ruleset...
      ruleset = "current"

      // ...and the later phases that would otherwise challenge the request.
      phases = [
        "http_request_firewall_managed",
        "http_request_sbfm", // Super bot fight mode (though not enabled now)
      ]

      // The legacy toggles live outside the phase model and must be named
      // individually. `bic` is Browser Integrity Check, which inspects headers
      // for browser-like plausibility; `securityLevel` blocks on IP reputation,
      // which datacentre addresses score badly on.
      products = [
        "bic",
        "securityLevel",
        "uaBlock",
      ]
    }

    // Surfaces the skip in Security Events, so a passing check is auditable.
    logging = {
      enabled = true
    }
  }]
}
