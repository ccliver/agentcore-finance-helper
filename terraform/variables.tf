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

variable "entra_tenant_id" {
  description = "Microsoft Entra Directory (tenant) ID."
  type        = string
}

variable "entra_client_id" {
  description = "Microsoft Entra Application (client) ID for the finance-helper-cli app registration."
  type        = string
}

variable "cli_callback_port" {
  description = "Local port the CLI listens on for the OAuth PKCE callback."
  type        = number
  default     = 9999
}
