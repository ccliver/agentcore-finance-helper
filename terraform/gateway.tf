data "archive_file" "tools" {
  type        = "zip"
  source_file = "${path.module}/../src/tools/lambda_handler.py"
  output_path = "${path.module}/tools.zip"
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "tools_lambda" {
  name               = "${var.agent_runtime_name}-tools-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_exec" {
  role       = aws_iam_role.tools_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "finance_tools" {
  function_name    = "${var.agent_runtime_name}-tools"
  role             = aws_iam_role.tools_lambda.arn
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.tools.output_path
  source_code_hash = data.archive_file.tools.output_base64sha256
}

data "aws_iam_policy_document" "gateway_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "gateway" {
  name               = "${var.agent_runtime_name}-gateway-role"
  assume_role_policy = data.aws_iam_policy_document.gateway_assume_role.json
}

resource "aws_iam_role_policy" "gateway_invoke_lambda" {
  role = aws_iam_role.gateway.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "lambda:InvokeFunction"
      Resource = aws_lambda_function.finance_tools.arn
    }]
  })
}

resource "aws_bedrockagentcore_gateway" "finance_helper" {
  name            = "${replace(var.agent_runtime_name, "_", "-")}-gateway"
  role_arn        = aws_iam_role.gateway.arn
  protocol_type   = "MCP"
  authorizer_type = "AWS_IAM"

  depends_on = [aws_iam_role_policy.gateway_invoke_lambda]

  protocol_configuration {
    mcp {
      supported_versions = ["2025-11-25"]
    }
  }
}

resource "aws_lambda_permission" "gateway" {
  statement_id  = "AllowGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finance_tools.function_name
  principal     = "bedrock-agentcore.amazonaws.com"
  source_arn    = aws_bedrockagentcore_gateway.finance_helper.gateway_arn
}

resource "aws_bedrockagentcore_gateway_target" "compound_interest" {
  gateway_identifier = aws_bedrockagentcore_gateway.finance_helper.gateway_id
  name               = "compound-interest"

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.finance_tools.arn

        tool_schema {
          inline_payload {
            name        = "compound_interest"
            description = "Calculate compound interest and return the final balance and total interest earned."

            input_schema {
              type = "object"
              property {
                name        = "principal"
                type        = "number"
                description = "Initial investment amount in dollars."
                required    = true
              }
              property {
                name        = "annual_rate"
                type        = "number"
                description = "Annual interest rate as a percentage (e.g. 5 for 5%)."
                required    = true
              }
              property {
                name        = "years"
                type        = "integer"
                description = "Number of years to compound."
                required    = true
              }
              property {
                name        = "compounds_per_year"
                type        = "integer"
                description = "How many times interest compounds per year (default 12)."
                required    = false
              }
              property {
                name        = "additional_monthly"
                type        = "number"
                description = "Fixed amount added each month (default 0)."
                required    = false
              }
            }
          }
        }
      }
    }
  }
}

resource "aws_bedrockagentcore_gateway_target" "loan_payment" {
  gateway_identifier = aws_bedrockagentcore_gateway.finance_helper.gateway_id
  name               = "loan-payment"

  credential_provider_configuration {
    gateway_iam_role {}
  }

  target_configuration {
    mcp {
      lambda {
        lambda_arn = aws_lambda_function.finance_tools.arn

        tool_schema {
          inline_payload {
            name        = "loan_payment"
            description = "Calculate the fixed monthly payment for a loan and total interest paid over the term."

            input_schema {
              type = "object"
              property {
                name        = "principal"
                type        = "number"
                description = "Loan amount in dollars."
                required    = true
              }
              property {
                name        = "annual_rate"
                type        = "number"
                description = "Annual interest rate as a percentage (e.g. 6 for 6%)."
                required    = true
              }
              property {
                name        = "years"
                type        = "integer"
                description = "Loan term in years."
                required    = true
              }
              property {
                name        = "compounds_per_year"
                type        = "integer"
                description = "Compounding periods per year (default 12)."
                required    = false
              }
            }
          }
        }
      }
    }
  }
}
