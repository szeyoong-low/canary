// A subnet group is the set of subnets RDS may place the instance in. RDS
// demands at least two Availability Zones even for a single-AZ instance: the
// second is what a later conversion to Multi-AZ would fail over into, so
// requiring it now avoids a rebuild then.
// https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html

resource "aws_db_subnet_group" "postgres" {
  name        = "postgres-${local.name_suffix}"
  subnet_ids  = module.vpc.private_subnets
  description = "Private subnets the ${local.environment} database may be placed in."

  tags = {
    function = "database"
  }
}

locals {
  postgres_port = 5432

  initial_storage = 20 // The floor RDS bills for

  // Ceiling for RDS's own storage autoscaling: grows the volume when the
  // instance runs short and never shrinks it again, so this is the ceiling on
  // storage bills. https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.Autoscaling.html
  maximum_storage = 100
  fixed_storage   = 0

  // Retained backups are free up to the size of allocated storage, so one day
  // in production costs nothing and buys point-in-time recovery. Zero disables
  // PITR entirely and forbids a final snapshot for disposable PR environments.
  production_backup_retention  = 1
  development_backup_retention = 0

  // UTC. Kept apart from each other, and both in the small hours so that a
  // future EventBridge stop/start schedule can be slotted around them.
  backup_window      = "03:00-04:00"
  maintenance_window = "sun:04:30-sun:05:30" // Stopped DB will always wake up for this
}

resource "aws_db_instance" "postgres" {
  identifier = "postgres-${local.name_suffix}"

  engine                     = "postgres"
  engine_version             = "18"
  auto_minor_version_upgrade = true

  instance_class = "db.t4g.micro"

  // Burstable Graviton. Its CPU credits accrue while idle and are spent under
  // load, which suits traffic that arrives in bursts between long quiet spells.

  allocated_storage     = local.initial_storage
  max_allocated_storage = local.is_production ? local.maximum_storage : local.fixed_storage

  // gp3 costs the same as gp2 and gives a higher 3,000 IOPS baseline than gp2's
  // 3 IOPS/GB, which at 20 GiB would be 60.
  storage_type = "gp3"

  // Free encryption at rest under the account's default AWS-managed key.
  storage_encrypted = true

  db_name  = "canary"
  username = "canary_admin"

  // RDS generates the password, stores it in a Secrets Manager secret it owns,
  // and rotates it. The value never enters Terraform state or a plan.
  // The cost is that the connection URL has to be assembled at runtime from
  // this secret plus the host and port below.
  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.database.id]

  publicly_accessible = false

  multi_az = false

  port = local.postgres_port

  backup_retention_period = local.is_production ? local.production_backup_retention : local.development_backup_retention
  backup_window           = local.backup_window
  maintenance_window      = local.maintenance_window
  copy_tags_to_snapshot   = true

  deletion_protection       = local.is_production
  skip_final_snapshot       = !local.is_production
  final_snapshot_identifier = local.is_production ? "postgres-${local.name_suffix}-final" : null

  // Applies changes during the next maintenance window in production, so a
  // parameter edit cannot reboot the instance in the middle of the day.
  apply_immediately = !local.is_production

  // RDS refuses to shrink storage if it would cause it to be full
  lifecycle {
    ignore_changes = [allocated_storage]
  }

  tags = {
    function = "database"
  }

  // This exists for the destroy graph, which runs in reverse: depending on the
  // sleep places this instance's deletion before it, so its elastic network
  // interface is already released by the time the sleep expires and Terraform
  // moves on to the security group and subnets that interface references.
  depends_on = [time_sleep.eni_release]
}
