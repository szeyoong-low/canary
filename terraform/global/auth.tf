locals {
  // The `aud` claim the backend requires on every access token.
  // An opaque identifier that is never fetched. A URL only because that is the
  // convention and because it guarantees global uniqueness.
  auth0_audience = "https://${local.backend_hostname}"

  // Wildcards in Auth0 callback URLs may only replace a whole subdomain label,
  // so `dev-*-canary.low-szeyoong.workers.dev` is not expressible.
  // Acceptable because the account owning that subdomain is mine and it never
  // appears in the production client.
  frontend_preview_origin  = "https://*.low-szeyoong.workers.dev"
  frontend_production_apex = "https://canary.markets"

  frontend_origins = [
    local.frontend_production_apex,
    "https://www.canary.markets",
    local.frontend_preview_origin,
    "http://localhost:5030",
    "http://127.0.0.1:5030",
  ]

  signing_algorithm = "RS256" // Asymmetric

  // Eight hours: long enough for a typical workday (that's a lie), short
  // enough that a leaked token expires within the day.
  access_token_ttl = 28800

  // Two weeks of inactivity ends the session; ninety days ends it regardless.
  idle_refresh_token_ttl = 1209600
  refresh_token_ttl      = 7776000

  auth_domain = "auth.canary.markets"
}


// The API being protected. Creating it is what makes Auth0 willing to mint
// access tokens carrying this audience. No scopes are declared, authentication-only
resource "auth0_resource_server" "api" {
  name       = "canary-api"
  identifier = local.auth0_audience

  signing_alg    = local.signing_algorithm
  token_lifetime = local.access_token_ttl

  // It exists to let a user approve a third party server's access to their data,
  // which is meaningless when the client and the API are first party.
  skip_consent_for_verifiable_first_party_clients = true
}


resource "auth0_client" "frontend" {
  name           = "Canary Terminal"
  app_type       = "spa"
  is_first_party = true

  grant_types = [
    "authorization_code",
    "refresh_token",
  ]

  oidc_conformant = true // Rejects legacy behaviours

  web_origins         = local.frontend_origins
  callbacks           = local.frontend_origins
  allowed_logout_urls = local.frontend_origins

  jwt_configuration {
    alg = local.signing_algorithm
  }

  refresh_token {
    // Refresh tokens live in browser storage, so they are assumed to leak.
    // Rotation issues a new one on every use and invalidates its predecessor,
    // which turns a stolen token into a detectable event: when the thief and
    // the real user both present the same token, Auth0 revokes the family.
    rotation_type   = "rotating"
    expiration_type = "expiring"
    leeway          = 0

    idle_token_lifetime = local.idle_refresh_token_ttl
    token_lifetime      = local.refresh_token_ttl
  }
}


// How the client proves who it is to redeem tokens from Auth0. Separate
// resource from the client itself because it is also where a confidential
// client's secret or signing key would live.
resource "auth0_client_credentials" "frontend" {
  client_id             = auth0_client.frontend.id
  authentication_method = "none" // PKCE used instead
}


// Username and password sign-in. Auth0 owns this user store and the local
// `app_user` row is keyed on the subject it issues.
resource "auth0_connection" "password" {
  name     = "canary-users"
  strategy = "auth0"

  options {
    password_policy        = "excellent"
    brute_force_protection = true
  }
}


resource "auth0_connection_clients" "password" {
  connection_id   = auth0_connection.password.id
  enabled_clients = [auth0_client.frontend.id]
}


resource "auth0_action" "profile_claims" {
  name = "Add profile claims in the ID token to the access token"

  runtime = "node22"
  code    = file("${path.module}/actions/profile-claims.js")
  deploy  = true

  supported_triggers {
    id      = "post-login"
    version = "v3"
  }
}


// Binds the Action into the login flow. Authoritative for the trigger's whole
// action list, in order.
resource "auth0_trigger_actions" "post_login" {
  trigger = "post-login"

  actions {
    id           = auth0_action.profile_claims.id
    display_name = auth0_action.profile_claims.name
  }
}


// Serve the login page and mints tokens from a domain I own.
// Moving off Auth0 later becomes a DNS change rather than a change to the `iss`
// every client and the backend agree on.
//
// This is why it must exist before first login. The issuer is baked into every
// token, so attaching a custom domain to a live tenant invalidates every token
// in flight and forces a coordinated frontend and backend redeploy.
resource "auth0_custom_domain" "auth" {
  domain = local.auth_domain
  type   = "auth0_managed_certs"
}

// Auth0 issues no certificate until it can see this record, which is how it
// checks the domain is actually mine.
resource "cloudflare_dns_record" "auth0_custom_domain" {
  zone_id = local.cloudflare_zone_id
  type    = "CNAME"
  name    = auth0_custom_domain.auth.verification[0].methods[0]["domain"]
  content = auth0_custom_domain.auth.verification[0].methods[0]["record"]
  proxied = false // Auth0 terminates TLS for this hostname itself
  ttl     = 1
}

// Separate from the domain because verification is an action taken against a
// resource that already exists, and it has to happen after DNS propagates.
resource "auth0_custom_domain_verification" "auth" {
  custom_domain_id = auth0_custom_domain.auth.id

  // Cloudflare serves the new record almost immediately, but Auth0's resolver
  // is not guaranteed to see it that fast.
  timeouts {
    create = "15m"
  }

  depends_on = [cloudflare_dns_record.auth0_custom_domain]
}


// Tenant-wide branding
resource "auth0_tenant" "canary" {
  friendly_name = "Canary"
  picture_url   = "${local.frontend_production_apex}/favicon.svg"
  support_email = "low.szeyoong@gmail.com"

  flags {
    enable_custom_domain_in_emails = true
  }

  depends_on = [auth0_custom_domain_verification.auth]
}
