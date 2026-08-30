// Supplied by the deployment workflow from the list of currently open pull requests.

variable "pull_request_numbers" {
  description = "Numbers of the pull requests that should have a development workspace."
  type        = set(string)
  default     = []
}
