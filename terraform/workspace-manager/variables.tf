// Supplied by the deployment workflow from the list of currently open pull requests.

variable "pull_request_numbers" {
  description = "Numbers of the pull requests that should have a development workspace."
  type        = set(string)
  default     = []
}

variable "PRODUCTION_BACKEND_SECRETS" {
  type        = map(string)
  description = "Environment values for the production backend."
  sensitive   = true
}

variable "DEVELOPMENT_BACKEND_SECRETS" {
  type        = map(string)
  description = "Environment values shared by every pull request backend."
  sensitive   = true
}

variable "CLOUDFLARE_API_TOKEN" {
  type        = string
  description = "Cloudflare API token with DNS edit rights on the canary.markets zone. Every workspace that writes a DNS record authenticates with this."
  sensitive   = true
}

