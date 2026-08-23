// Created in the console and adopted here read-only, on the same terms as the
// bootstrap roles: bootstrap-boundary's DenyManagingSelfAndBoundaries statement
// denies this workspace every IAM write against it, so Terraform can read and
// refresh it but can never modify or destroy it.

import {
  to = aws_iam_policy.workspace_boundary
  id = local.workspace_boundary_arn
}

resource "aws_iam_policy" "workspace_boundary" {
  name = local.workspace_boundary_name

  tags = {
    wildcard-allow = "intentional-permissions-boundary"
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "GuardrailOnlyDoesNotLimit"
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      },
      {
        Sid      = "CannotPassRolesToUnboundedServices"
        Effect   = "Deny"
        Action   = "iam:PassRole"
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "iam:PermissionsBoundary" = local.workspace_boundary_arn
          }
        }
      },
      {
        Sid    = "CannotManageOIDCRolesOrBoundaries"
        Effect = "Deny"
        Action = "iam:*"
        Resource = [
          "${local.role_arn_prefix}/${local.role_name_prefix}-*",
          local.bootstrap_boundary_arn,
          local.workspace_boundary_arn,
        ]
      },
      {
        Sid    = "PrincipalsCreatedInheritBoundary"
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:CreateUser",
          "iam:PutRolePermissionsBoundary",
          "iam:PutUserPermissionsBoundary",
        ]
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "iam:PermissionsBoundary" = local.workspace_boundary_arn
          }
        }
      },
      {
        Sid    = "CannotRemoveBoundaries"
        Effect = "Deny"
        Action = [
          "iam:DeleteRolePermissionsBoundary",
          "iam:DeleteUserPermissionsBoundary",
        ]
        Resource = "*"
      },
      {
        Sid    = "DenyAccountLevelOrAuditChanges"
        Effect = "Deny"
        Action = [
          "organizations:*",
          "account:*",
          "iam:CreateOpenIDConnectProvider",
          "iam:DeleteOpenIDConnectProvider",
          "iam:UpdateOpenIDConnectProviderThumbprint",
          "iam:CreateSAMLProvider",
          "iam:DeleteSAMLProvider",
          "iam:CreateAccountAlias",
          "iam:DeleteAccountAlias",
          "iam:UpdateAccountPasswordPolicy",
          "cloudtrail:StopLogging",
          "cloudtrail:DeleteTrail",
        ]
        Resource = "*"
      },
      {
        Sid      = "DenyCrossEnvironmentResourceAccess"
        Effect   = "Deny"
        Action   = "*"
        Resource = "*"
        Condition = {
          StringNotEqualsIfExists = {
            "aws:ResourceTag/environment" = "$${aws:PrincipalTag/environment}"
          }
        }
      },
      {
        Sid      = "DenyForeignEnvironmentTagOnCreation"
        Effect   = "Deny"
        Action   = "*"
        Resource = "*"
        Condition = {
          StringNotEqualsIfExists = {
            "aws:RequestTag/environment" = "$${aws:PrincipalTag/environment}"
          }
        }
      },
      {
        Sid    = "DenyUntaggedPrincipalCreation"
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:CreateUser",
        ]
        Resource = "*"
        Condition = {
          Null = {
            "aws:RequestTag/environment" = "true"
          }
        }
      },
      {
        Sid      = "DenyEnvironmentTagRemoval"
        Effect   = "Deny"
        Action   = "*"
        Resource = "*"
        Condition = {
          "ForAnyValue:StringEquals" = {
            "aws:TagKeys" = "environment"
          }
          Null = {
            "aws:RequestTag/environment" = "true"
          }
        }
      },
    ]
  })
}
