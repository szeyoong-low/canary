resource "aws_ecr_repository" "backend" {
  name = "canary-backend"

  image_tag_mutability = "IMMUTABLE"

  # Findings are advisory and don't gate uploads.
  image_scanning_configuration {
    scan_on_push = true
  }

  # Encryption is left at the default AES256.

  # Holds production images.
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    function = "storage"
  }
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  # Rules are evaluated in ascending priority order.
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after a day."

        # Untagged images are manifests orphaned when a tag moved off them.
        # Nothing can reference these, so they are pure storage cost.
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }

        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Keep the last three production images as the rollback window."

        # `release-*` matches only promoted images. Development images carry a
        # `dev-n-` prefix and so cannot be counted here.
        selection = {
          tagStatus      = "tagged"
          tagPatternList = ["release-*"]
          countType      = "imageCountMoreThan"
          countNumber    = 3
        }

        action = { type = "expire" }
      },
    ]
  })
}
