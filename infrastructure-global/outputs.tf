output "backend_repository_arn" {
  description = "ARN of the backend container registry, for IAM policies that scope access to it."
  value       = aws_ecr_repository.backend.arn
}

output "backend_repository_url" {
  description = "Registry URL of the backend container repository, for `docker push` and the ECS task definition's image reference."
  value       = aws_ecr_repository.backend.repository_url
}
