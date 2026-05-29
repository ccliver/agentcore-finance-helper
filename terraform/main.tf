data "aws_iam_policy_document" "assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "runtime_permissions" {
  statement {
    sid       = "ECRAuth"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "ECRPull"
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchCheckLayerAvailability",
    ]
    resources = [aws_ecr_repository.finance_helper.arn]
  }

  statement {
    sid     = "BedrockInvoke"
    effect  = "Allow"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [
      "arn:aws:bedrock:*::foundation-model/anthropic.claude-haiku-4-5*",
      "arn:aws:bedrock:*:*:inference-profile/us.anthropic.claude-haiku-4-5*",
    ]
  }

  statement {
    sid       = "MemoryAccess"
    effect    = "Allow"
    actions   = ["bedrock-agentcore:*"]
    resources = [aws_bedrockagentcore_memory.finance_helper.arn]
  }

  statement {
    sid       = "SSMReadMemoryId"
    effect    = "Allow"
    actions   = ["ssm:GetParameter"]
    resources = ["arn:aws:ssm:${var.aws_region}:*:parameter/agentcore-finance-helper/memory-id"]
  }
}

resource "aws_iam_role" "agentcore_runtime" {
  name               = "${var.agent_runtime_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_iam_role_policy" "agentcore_runtime" {
  role   = aws_iam_role.agentcore_runtime.id
  policy = data.aws_iam_policy_document.runtime_permissions.json
}

resource "aws_ecr_repository" "finance_helper" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_bedrockagentcore_memory" "finance_helper" {
  name                  = "${var.agent_runtime_name}_memory"
  event_expiry_duration = var.memory_event_expiry_days
}

resource "aws_ssm_parameter" "memory_id" {
  name  = "/agentcore-finance-helper/memory-id"
  type  = "String"
  value = aws_bedrockagentcore_memory.finance_helper.id
}

resource "aws_ssm_parameter" "cli_config" {
  name = "/agentcore-finance-helper/cli-config"
  type = "String"
  value = jsonencode({
    tenant_id     = var.entra_tenant_id
    client_id     = var.entra_client_id
    runtime_arn   = aws_bedrockagentcore_agent_runtime.finance_helper.agent_runtime_arn
    callback_port = var.cli_callback_port
  })
}

resource "aws_bedrockagentcore_agent_runtime" "finance_helper" {
  agent_runtime_name = var.agent_runtime_name
  role_arn           = aws_iam_role.agentcore_runtime.arn

  depends_on = [aws_iam_role_policy.agentcore_runtime]

  agent_runtime_artifact {
    container_configuration {
      container_uri = "${aws_ecr_repository.finance_helper.repository_url}:${var.image_tag}"
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  authorizer_configuration {
    custom_jwt_authorizer {
      discovery_url    = "https://login.microsoftonline.com/${var.entra_tenant_id}/v2.0/.well-known/openid-configuration"
      allowed_audience = [var.entra_client_id]
    }
  }
}
