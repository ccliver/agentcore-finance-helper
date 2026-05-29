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
