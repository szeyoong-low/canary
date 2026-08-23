resource "aws_iam_openid_connect_provider" "hcp_terraform" {
  url             = local.hcp_oidc_provider_url
  client_id_list  = [local.hcp_audience]
  thumbprint_list = ["06b25927c42a721631c1efd9431e648fa62e1e39"]

  tags = local.read_only_tags
}
