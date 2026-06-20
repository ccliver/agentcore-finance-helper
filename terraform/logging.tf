data "aws_caller_identity" "current" {}

resource "aws_cloudwatch_log_group" "runtime" {
  name              = "/agentcore/${var.agent_runtime_name}/runtime"
  retention_in_days = 7
}

# Allows the CloudWatch log delivery service to write to the log group.
resource "aws_cloudwatch_log_resource_policy" "runtime_delivery" {
  policy_name = "${var.agent_runtime_name}-delivery"
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "delivery.logs.amazonaws.com" }
      Action    = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource  = "${aws_cloudwatch_log_group.runtime.arn}:*"
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

resource "aws_cloudwatch_log_delivery_destination" "runtime" {
  name = "${var.agent_runtime_name}-runtime-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.runtime.arn
  }
}

resource "aws_cloudwatch_log_delivery_source" "runtime" {
  name         = "${var.agent_runtime_name}-runtime"
  resource_arn = aws_bedrockagentcore_agent_runtime.finance_helper.agent_runtime_arn
  log_type     = "APPLICATION_LOGS"
}

resource "aws_cloudwatch_log_delivery" "runtime" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.runtime.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.runtime.arn
}

# Gateway log delivery
resource "aws_cloudwatch_log_group" "gateway" {
  name              = "/agentcore/${var.agent_runtime_name}/gateway"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_resource_policy" "gateway_delivery" {
  policy_name = "${var.agent_runtime_name}-gateway-delivery"
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "delivery.logs.amazonaws.com" }
      Action    = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource  = "${aws_cloudwatch_log_group.gateway.arn}:*"
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

resource "aws_cloudwatch_log_delivery_destination" "gateway" {
  name = "${var.agent_runtime_name}-gateway-logs"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.gateway.arn
  }
}

resource "aws_cloudwatch_log_delivery_source" "gateway" {
  name         = "${var.agent_runtime_name}-gateway"
  resource_arn = aws_bedrockagentcore_gateway.finance_helper.gateway_arn
  log_type     = "APPLICATION_LOGS"
}

resource "aws_cloudwatch_log_delivery" "gateway" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.gateway.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.gateway.arn
}
