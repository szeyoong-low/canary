variable "BACKEND_SECRETS" {
  type        = map(string)
  description = "Every environment value the backend reads"
  sensitive   = true

  validation {
    // A missing key does not fail here by default: it fails at container start,
    // as a pydantic ValidationError in CloudWatch, after ECS has cycled the task
    // several times.
    //
    // The message cannot name which keys are missing. Terraform treats anything
    // derived from a sensitive value as sensitive, and an error message may not be.
    condition = length(setsubtract(
      [
        "ALLOW_ORIGINS",
        "ALLOW_ORIGIN_REGEX",
        "FMP_API_KEY",
        "FMP_BASE_URL",
        "OPENROUTER_API_KEY",
        "PLANNING_NODE_MODEL",
        "PLANNING_NODE_PROVIDER",
      ],
      keys(var.BACKEND_SECRETS)
    )) == 0

    error_message = "BACKEND_SECRETS must contain every field on the backend's settings model"
  }
}

locals {
  production_secret_recovery  = 30
  development_secret_recovery = 0
}

// One secret per environment holding every environment value as a JSON object,
// sensitive or not.
resource "aws_secretsmanager_secret" "backend" {
  name        = "backend-${local.name_suffix}"
  description = "Environment values for the ${local.environment} backend."

  recovery_window_in_days = local.is_production ? local.production_secret_recovery : local.development_secret_recovery

  tags = {
    function = "secret"
  }
}

resource "aws_secretsmanager_secret_version" "backend" {
  secret_id = aws_secretsmanager_secret.backend.id

  // Keys carry through to the task definition, which maps each one to the
  // uppercase environment variable the settings model reads it from.
  //
  // These values land verbatim in Terraform state. That is acceptable only
  // because state lives in HCP Terraform, which encrypts it at rest.
  secret_string = jsonencode(var.BACKEND_SECRETS)
}
