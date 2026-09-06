output "backend_repository_arn" {
  description = "ARN of the backend container registry, for IAM policies that scope access to it."
  value       = aws_ecr_repository.backend.arn
}

output "backend_repository_url" {
  description = "Registry URL of the backend container repository, for `docker push` and the ECS task definition's image reference."
  value       = aws_ecr_repository.backend.repository_url
}

output "backend_hostname" {
  description = "The apex domain of the backend API"
  value       = local.backend_hostname
}

output "api_tls_certificate_arn" {
  description = "ARN of the issued wildcard certificate for the backend API, for each environment's HTTPS listener. Reads through the validation resource so consumers cannot attach it before ACM has issued it."
  value       = aws_acm_certificate_validation.api.certificate_arn
}

output "cloudflare_zone_id" {
  description = "Zone that owns canary.markets, for each environment's own DNS record. Read from here rather than restated per workspace so the zone has one definition."
  value       = local.cloudflare_zone_id
}

output "auth0_issuer" {
  description = "The `iss` claim the backend must require on every access token. Trailing slash included: Auth0 mints it that way and the comparison is exact."
  value       = "https://${auth0_custom_domain.auth.domain}/"

  // The domain attribute is known before Auth0 has certified anything, so the
  // dependency has to be stated rather than implied through a reference.
  // Without it a consumer could wire up an issuer that does not yet serve JWKS.
  depends_on = [auth0_custom_domain_verification.auth]
}

output "auth0_audience" {
  description = "The `aud` claim the backend must require, which is the API's identifier."
  value       = auth0_resource_server.api.identifier
}

output "auth0_frontend_client_id" {
  description = "For frontend's Auth0 SDK configuration. Identifies the client and does not authenticate it."
  value       = auth0_client.frontend.client_id
}
