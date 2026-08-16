locals {
  env         = terraform.workspace # "production" or "development-pr-n"
  is_prod     = local.env == "production"
  name_suffix = local.env # for global/regional/account-level uniqueness
}