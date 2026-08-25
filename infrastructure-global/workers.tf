locals {
  cloudflare_account_id = "186e5cb41a4496f3fe4621133cbfb8b6"
}

# Delete the import block once this has been applied. It is a one-shot
# instruction, not part of the desired state.
import {
  to = cloudflare_worker.frontend
  id = "186e5cb41a4496f3fe4621133cbfb8b6/ee940cdd36fb411387fc12ea1d1ad0c3"
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
    # This one setting is also spelled `preview_urls` in frontend/wrangler.toml,
    # so the two must agree. Both are currently true. If they ever diverge,
    # whichever tool ran last wins.
    previews_enabled = true
  }

  # The Worker becomes the production frontend once its custom domain is
  # attached, so removing this resource must never be a silent side effect of
  # editing the configuration.
  lifecycle {
    prevent_destroy = true
  }
}
