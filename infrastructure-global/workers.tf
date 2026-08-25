locals {
  cloudflare_account_id = "186e5cb41a4496f3fe4621133cbfb8b6"
}

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

  # The Worker becomes the production frontend once its custom domain is
  # attached, so removing this resource must never be a silent side effect of
  # editing the configuration.
  lifecycle {
    prevent_destroy = true
  }
}
