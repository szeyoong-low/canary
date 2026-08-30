resource "aws_cloudwatch_log_group" "backend" {
  // The `/ecs/` prefix is convention to group every container log stream under
  // one path in the console.
  name = "/ecs/backend-${local.name_suffix}"

  // A preview environment never outlives its pull request, so a month of
  // history buys nothing. Ingestion dominates the bill either way.
  retention_in_days = local.is_production ? 30 : 3

  tags = {
    function = "observability"
  }
}
