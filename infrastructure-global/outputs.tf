output "backend_repository_arn" {
  description = "ARN of the backend container registry, for IAM policies that scope access to it."
  value       = aws_ecr_repository.backend.arn
}

output "backend_repository_url" {
  description = "Registry URL of the backend container repository, for `docker push` and the ECS task definition's image reference."
  value       = aws_ecr_repository.backend.repository_url
}

output "api_tls_certificate_arn" {
  description = "ARN of the issued wildcard certificate for the backend API, for each environment's HTTPS listener. Reads through the validation resource so consumers cannot attach it before ACM has issued it."
  value       = aws_acm_certificate_validation.api.certificate_arn
}
