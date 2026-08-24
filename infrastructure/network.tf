variable "vpc_cidr" {
  type        = string
  description = "IPv4 address range for this environment's VPC, in CIDR notation."
  default     = "10.0.0.0/16"

  validation {
    // cidrnetmask is called for its error, not its result: it raises on anything
    // that is not IPv4 CIDR, and `can` turns that into false. Rejecting IPv6 here
    // is deliberate, matching the IPv4-only decision in the ADR.
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be valid IPv4 CIDR notation."
  }

  validation {
    // AWS only allows VPC CIDRs between /16 and /28
    // As outlined in the documentation, I want 4 bits reserved for subnets and
    // 8 bits for host. I could allow it to vary, but I will make it constant
    // for simplicity.
    condition     = endswith(var.vpc_cidr, "/16")
    error_message = "vpc_cidr must be a /16."
  }
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability Zones to lay subnets out across, in a fixed order."

  // Pinned rather than read from the aws_availability_zones data source: that
  // source's ordering is not contractually stable, and the VPC module pairs
  // subnets to AZs by list position. A reorder would silently destroy and
  // recreate every subnet.
  //
  // For the same reason, only ever APPEND to this list. Removing an entry from
  // the middle shifts every later index onto the wrong AZ.
  default = ["eu-west-2a", "eu-west-2b"]

  validation {
    condition     = length(var.availability_zones) >= 2
    error_message = "At least two Availability Zones are required for an Application Load Balancer."
  }
}

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

  map_public_ip_on_launch = false

  // Toggle when needed as both cost money to leave running
  create_igw         = false
  enable_nat_gateway = false
}
