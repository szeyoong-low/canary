locals {
  subnet_bits         = 4
  private_tier_offset = 8

  // Position i in each list pairs with position i in var.availability_zones:
  // the VPC module matches subnets to AZs by index, not by name.
  public_subnets  = [for i, az in var.availability_zones : cidrsubnet(var.vpc_cidr, local.subnet_bits, i)]
  private_subnets = [for i, az in var.availability_zones : cidrsubnet(var.vpc_cidr, local.subnet_bits, i + local.private_tier_offset)]
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.7"

  name = "vpc-${local.name_suffix}"
  cidr = var.vpc_cidr

  tags = {
    "function" : "network"
  }

  // The module pairs these three lists BY POSITION, not by name: public_subnets[1]
  // lands in azs[1]. All three are derived from var.availability_zones so they
  // cannot fall out of step with each other.
  azs             = var.availability_zones
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets

  // Required for RDS and VPC interface endpoints to resolve to their private
  // addresses from inside the VPC.
  enable_dns_hostnames = true
  enable_dns_support   = true

  // Resources that interact with the public Internet need a public IP address or ENI.
  // However, individual resources should opt in.
  map_public_ip_on_launch = false

  // Creating it also adds the 0.0.0.0/0 route to the public route table, which
  // is what lets a task reach ECR, Secrets Manager, and CloudWatch Logs.
  create_igw = true

  enable_nat_gateway = false
}
