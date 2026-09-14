variable "image_tag" {
  type        = string
  description = "Tag of the image in the backend repository to run: the tip commit SHA of the branch this environment tracks, under the prefix its pipeline pushed it with."

  validation {
    // The realistic failure is an empty value, which arrives when the upstream
    // build was skipped. The prefix convention belongs to the pipeline.
    condition     = length(trimspace(var.image_tag)) > 0
    error_message = "image_tag must not be empty."
  }
}

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

variable "BACKEND_SECRETS" {
  type        = map(string)
  description = "Every environment value the backend reads"
  sensitive   = true

  validation {
    // A missing key does not fail here by default: it fails at container start,
    // as a pydantic ValidationError in CloudWatch, after ECS has cycled the task
    // several times.
    //
    // The message cannot name which keys are missing. Terraform treats anything
    // derived from a sensitive value as sensitive, and an error message may not be.
    condition = length(setsubtract(
      [
        "ALLOW_ORIGINS",
        "ALLOW_ORIGIN_REGEX",
        "FMP_API_KEY",
        "FMP_BASE_URL",
        "OPENROUTER_API_KEY",
        "PLANNING_NODE_MODEL",
        "PLANNING_NODE_PROVIDER",
      ],
      keys(var.BACKEND_SECRETS)
    )) == 0

    error_message = "BACKEND_SECRETS must contain every field on the backend's settings model"
  }
}