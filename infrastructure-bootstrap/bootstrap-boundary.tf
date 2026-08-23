resource "aws_iam_policy" "bootstrap_boundary" {
  name = local.bootstrap_boundary_name

  tags = local.read_only_tags

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadIAM"
        Effect = "Allow"
        Action = [
          "iam:Get*",
          "iam:List*",
        ]
        Resource = "*"
      },
      {
        Sid    = "ManageWorkspaceRoles"
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:UpdateRole",
          "iam:UpdateRoleDescription",
          "iam:UpdateAssumeRolePolicy",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:PutRolePermissionsBoundary",
        ]
        Resource = "${local.role_arn_prefix}/${local.role_name_prefix}-*"
      },
      {
        Sid    = "ManageWorkspacePolicies"
        Effect = "Allow"
        Action = [
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:CreatePolicyVersion",
          "iam:DeletePolicyVersion",
          "iam:SetDefaultPolicyVersion",
          "iam:TagPolicy",
          "iam:UntagPolicy",
        ]
        Resource = "${local.policy_arn_prefix}/canary-*"
      },
      {
        Sid    = "DenyManagingSelfAndBoundaries"
        Effect = "Deny"
        NotAction = [
          "iam:Get*",
          "iam:List*",
        ]
        Resource = [
          "${local.role_arn_prefix}/${local.role_name_prefix}-*-${local.bootstrap_environment}",
          local.bootstrap_boundary_arn,
          local.workspace_boundary_arn,
        ]
      },
      {
        Sid    = "RolesCreatedMustHaveWorkspaceBoundary"
        Effect = "Deny"
        Action = [
          "iam:CreateRole",
          "iam:PutRolePermissionsBoundary",
        ]
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "iam:PermissionsBoundary" = local.workspace_boundary_arn
          }
        }
      },
      {
        Sid      = "CannotDeleteBoundaries"
        Effect   = "Deny"
        Action   = "iam:DeleteRolePermissionsBoundary"
        Resource = "*"
      },
      {
        Sid    = "CannotAlterOIDCIdentityProviders"
        Effect = "Deny"
        Action = [
          "iam:CreateOpenIDConnectProvider",
          "iam:DeleteOpenIDConnectProvider",
          "iam:UpdateOpenIDConnectProviderThumbprint",
          "iam:AddClientIDToOpenIDConnectProvider",
          "iam:RemoveClientIDFromOpenIDConnectProvider",
        ]
        Resource = "*"
      },
    ]
  })
}
