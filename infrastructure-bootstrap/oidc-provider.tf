resource "aws_iam_openid_connect_provider" "hcp_terraform" {
  url             = local.hcp_oidc_provider_url
  client_id_list  = [local.hcp_audience]

  tags = local.read_only_tags
}

resource "aws_iam_openid_connect_provider" "github_actions" {
  url            = local.github_oidc_provider_url
  client_id_list = [local.github_audience]

  tags = local.read_only_tags
}

import {
  to = aws_iam_openid_connect_provider.github_actions
  id = "${local.arn_prefix}${data.aws_caller_identity.current.account_id}:oidc-provider/${trimprefix(local.github_oidc_provider_url, "https://")}"
}
