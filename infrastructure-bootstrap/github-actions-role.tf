// Lives here rather than in the workspace that owns the registry because
// every IAM principal in this account is created by the bootstrap workspace,
// under a boundary the environment workspaces are denied from touching.

data "aws_region" "current" {}

locals {
  // Hand-assembled rather than read off the resource, because the repository is
  // declared in the `global` workspace. Reading it would close a dependency
  // loop: `global` cannot run without a role from here, and this could not plan
  // without an output from there.
  // Renaming the repository breaks this policy silently instead:
  // pushes fail with AccessDenied, not with a missing repository.
  backend_repository_name = "canary-backend"

  backend_repository_arn = join(":", [
    "arn:aws:ecr",
    data.aws_region.current.region,
    data.aws_caller_identity.current.account_id,
    "repository/${local.backend_repository_name}",
  ])

  // Both halves of the image lifecycle run on `pull_request` events.
  // GitHub presents the same subject for both with no branch component, so one
  // exact match covers both. A push to `main` presents a different subject and is refused.
  github_pull_request_subject = "repo:${local.github_repository}:pull_request"
}

resource "aws_iam_role" "github_actions_ecr" {
  name = "${local.github_role_name_prefix}-ecr"
  permissions_boundary = aws_iam_policy.workspace_boundary.arn

  tags = {
    function = "cicd-pipeline"
  }

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github_actions.arn
      }

      Action = local.github_assume_role_action

      Condition = {
        StringEquals = {
          (local.github_audience_claim) = local.github_audience
          (local.github_subject_claim)  = local.github_pull_request_subject
        }
      }
    }]
  })
}

// Inline rather than a managed policy: it is single-use, and the nearest
// AWS-managed equivalent (AmazonEC2ContainerRegistryPowerUser) grants its
// verbs across every repository in the account.

resource "aws_iam_role_policy" "publish_backend_image" {
  name = "publish-backend-image"
  role = aws_iam_role.github_actions_ecr.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        // An account-level call that exchanges the assumed session for a
        // registry password. It takes no resource, so `*` is the only value
        // that works.
        Sid      = "AuthenticateToRegistry"
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Sid    = "PushImageLayersAndManifests"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
        ]
        Resource = local.backend_repository_arn
      },
      {
        // Reads, for two jobs: deciding whether this commit's tag already
        // exists before rebuilding it, and fetching the manifest of a
        // development image so promotion can re-put it under a release tag.
        Sid    = "InspectImagesForIdempotencyAndPromotion"
        Effect = "Allow"
        Action = [
          "ecr:DescribeImages",
          "ecr:ListImages",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
        ]
        Resource = local.backend_repository_arn
      },
      {
        // Pruning development images is exclusively the pipeline's job: the
        // lifecycle policy cannot express "one image per pull request", and
        // promotion has to drop the development tag it was lifted from.
        Sid      = "PruneDevelopmentAndSupersededTags"
        Effect   = "Allow"
        Action   = "ecr:BatchDeleteImage"
        Resource = local.backend_repository_arn
      },
    ]
  })
}

resource "aws_iam_role_policy_attachments_exclusive" "github_actions_ecr" {
  role_name   = aws_iam_role.github_actions_ecr.name
  policy_arns = []
}

resource "aws_iam_role_policies_exclusive" "github_actions_ecr" {
  role_name    = aws_iam_role.github_actions_ecr.name
  policy_names = [aws_iam_role_policy.publish_backend_image.name]
}
