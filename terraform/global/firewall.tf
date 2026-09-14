// One ruleset owns the whole http_ratelimit phase for the zone: Cloudflare
// allows a single ruleset per phase, so every rate limiting rule lives here.
resource "cloudflare_ruleset" "rate_limit" {
  zone_id     = local.cloudflare_zone_id
  name        = "Backend API rate limits"
  kind        = "zone"
  phase       = "http_ratelimit"
  description = "Managed in terraform/global/waf.tf"

  rules = [{
    description = "Cap requests per IP to the backend API"

    expression = "http.host eq \"${local.backend_hostname}\""

    // A managed challenge is a 403 whose body is an HTML interstitial with
    // JavaScript that has to execute, pass, and then re-issue the original
    // request. That works on a top-level navigation, because the browser
    // renders the response and runs the script.
    // The frontend calls this API with fetch from already-running JS. The HTML
    // comes back as a string into a .json() that then throws.
    action = "block"

    ratelimit = {
      // Per-IP, counted per data centre. This pairing is the only one
      // non-Enterprise plans allow, so the real ceiling is this limit times
      // the number of colocations an attacker spreads across. It is a blunt
      // cost guardrail, not a precise security boundary.
      characteristics = ["ip.src", "cf.colo.id"]

      period              = 60
      requests_per_period = 30

      // How long the 429 lasts once tripped, not how long counting lasts.
      mitigation_timeout = 60
    }
  }]
}
