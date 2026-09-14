variable "GITHUB_OAUTH_CLIENT_ID" {
  description = "Client ID of the GitHub OAuth App. Public: it appears in the authorise URL the browser is redirected to."
  type        = string
}

variable "GITHUB_OAUTH_CLIENT_SECRET" {
  description = "Client secret of the GitHub OAuth App. Auth0 presents it to GitHub when exchanging the authorisation code for an access token."
  type        = string
  sensitive   = true
}

variable "GOOGLE_OAUTH_CLIENT_ID" {
  description = "Client ID of the Google Cloud OAuth 2.0 client. Public: it appears in the authorise URL."
  type        = string
}

variable "GOOGLE_OAUTH_CLIENT_SECRET" {
  description = "Client secret of the Google Cloud OAuth 2.0 client."
  type        = string
  sensitive   = true
}
