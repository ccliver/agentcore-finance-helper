variable "aws_region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "us-east-1"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository for the finance-helper container image."
  type        = string
  default     = "agentcore-finance-helper"
}

variable "agent_runtime_name" {
  description = "Name of the AgentCore Runtime."
  type        = string
  default     = "finance_helper"
}

variable "image_tag" {
  description = "Docker image tag to deploy to AgentCore Runtime."
  type        = string
  default     = "latest"
}

variable "memory_event_expiry_days" {
  description = "How long AgentCore Memory retains conversation events (days)."
  type        = number
  default     = 90
}

variable "cognito_user_email" {
  description = "Email address for the initial Cognito user created by Terraform."
  type        = string
}

variable "cognito_domain_prefix" {
  description = "Globally unique prefix for the Cognito hosted UI domain (e.g. finance-helper-abc123)."
  type        = string
  default     = "finance-helper-aizahx"
}

variable "cli_callback_port" {
  description = "Local port the CLI listens on for the OAuth PKCE callback."
  type        = number
  default     = 9999
}
