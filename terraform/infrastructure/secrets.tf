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
