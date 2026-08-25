resource "cloudflare_worker" "frontend" {
  account_id = local.cloudflare_account_id
  name       = "canary"

  subdomain = {
    # Serves the Worker at canary.low-szeyoong.workers.dev.
    enabled = true

    # Required for `wrangler versions upload --preview-alias`, which is how
    # pull requests get a stable dev-<n>-canary.low-szeyoong.workers.dev URL.
    #
    # Terraform is the sole owner. Wrangler only asserts this field when
    # `preview_urls` appears in wrangler.toml, where it is deliberately absent.
    #
    # Note that Wrangler does still force `enabled` above to true on every
    # `wrangler deploy`, because it defaults workers_dev to true whenever the
    # configuration declares no routes.
    previews_enabled = true
  }

  # Non-versioned settings, so both Wrangler and Terraform can write them.
  # These values mirror `[observability]` in frontend/wrangler.toml exactly.
  # They must be kept in sync: whichever tool runs last wins, and a mismatch
  # makes the two fight on every deploy.
  #
  # Declaring this is not optional. Left unset, Terraform plans
  # `enabled = true -> false` and switches Workers Logs off on the next apply.
  observability = {
    enabled = true

    # 1 means every request. Traffic is low enough that sampling would only
    # cost us the one log we wanted.
    head_sampling_rate = 1

    logs = {
      enabled            = true
      head_sampling_rate = 1
      invocation_logs    = true
      persist            = true
    }

    # Tracing is off. It is declared anyway so the intent is recorded rather
    # than inherited from whatever the API last returned.
    #
    # Note the absent `propagation_policy`. The account is not entitled to the
    # trace propagation feature, and sending the field at all returns
    # 403 code 100342. Omitting it here is necessary but NOT sufficient: the
    # attribute is optional+computed, so an unset config value falls back to
    # the prior state value rather than to null. The stale "authenticated"
    # already in state has to be scrubbed out once by hand.
    # See https://github.com/cloudflare/terraform-provider-cloudflare/issues/7211
    traces = {
      enabled            = false
      head_sampling_rate = 1
      persist            = true
    }
  }

  # The Worker becomes the production frontend once its custom domain is
  # attached, so removing this resource must never be a silent side effect of
  # editing the configuration.
  lifecycle {
    prevent_destroy = true
  }
}

resource "cloudflare_workers_custom_domain" "apex" {
  account_id = local.cloudflare_account_id
  zone_id    = local.cloudflare_zone_id
  hostname   = "canary.markets"
  service    = cloudflare_worker.frontend.name
}

resource "cloudflare_workers_custom_domain" "www" {
  account_id = local.cloudflare_account_id
  zone_id    = local.cloudflare_zone_id
  hostname   = "www.canary.markets"
  service    = cloudflare_worker.frontend.name
}
