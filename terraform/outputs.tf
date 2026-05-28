output "ecr_repository_url" {
  description = "ECR repository URL for the finance-helper image."
  value       = aws_ecr_repository.finance_helper.repository_url
}

output "agent_runtime_id" {
  description = "AgentCore Runtime ID (use with the AWS CLI to invoke the runtime)."
  value       = aws_bedrockagentcore_agent_runtime.finance_helper.agent_runtime_id
}

output "agent_runtime_arn" {
  description = "AgentCore Runtime ARN."
  value       = aws_bedrockagentcore_agent_runtime.finance_helper.agent_runtime_arn
}

output "memory_id" {
  description = "AgentCore Memory ID for conversation history."
  value       = aws_bedrockagentcore_memory.finance_helper.id
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID."
  value       = aws_cognito_user_pool.finance_helper.id
}

output "cognito_client_id" {
  description = "Cognito App Client ID for the CLI."
  value       = aws_cognito_user_pool_client.cli.id
}

output "cognito_issuer_url" {
  description = "OIDC issuer URL for the Cognito User Pool."
  value       = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.finance_helper.id}"
}

output "cognito_user_password" {
  description = "Generated password for the initial Cognito user (retrieve with: terraform output -raw cognito_user_password)."
  value       = random_password.cognito_user.result
  sensitive   = true
}

output "cognito_domain" {
  description = "Cognito hosted UI domain."
  value       = "https://${var.cognito_domain_prefix}.auth.${var.aws_region}.amazoncognito.com"
}
