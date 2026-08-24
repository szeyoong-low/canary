resource "aws_iam_policy" "workspace_boundary" {
  name = local.workspace_boundary_name

  tags = merge(local.read_only_tags, {
    wildcard-allow = "intentional-permissions-boundary"
  })

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
          StringNotEquals = {
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
          StringNotEquals = {
            "aws:RequestTag/environment" = "$${aws:PrincipalTag/environment}"
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
