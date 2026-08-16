provider "aws" {
  region = "eu-west-2" // London

  default_tags {
    tags = {
      managed_by  = "terraform"
      environment = local.env
    }
  }
}