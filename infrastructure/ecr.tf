# data "tfe_outputs" "global" {
#   organization = "CanaryMarkets"
#   workspace    = "global"
# }

# locals {
#   backend_repository_url = data.tfe_outputs.global.nonsensitive_values.backend_repository_url
# }
