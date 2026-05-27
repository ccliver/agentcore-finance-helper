# AgentCore Demo Running Financial Chat App

[![CI](https://github.com/ccliver/agentcore-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/ccliver/agentcore-demo/actions/workflows/ci.yml)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6, >= 6.21 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 6, >= 6.21 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [aws_bedrockagentcore_agent_runtime.finance_helper](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/bedrockagentcore_agent_runtime) | resource |
| [aws_bedrockagentcore_memory.finance_helper](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/bedrockagentcore_memory) | resource |
| [aws_ecr_repository.finance_helper](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository) | resource |
| [aws_iam_role.agentcore_runtime](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.agentcore_runtime](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_ssm_parameter.memory_id](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |
| [aws_iam_policy_document.assume_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.runtime_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_agent_runtime_name"></a> [agent\_runtime\_name](#input\_agent\_runtime\_name) | Name of the AgentCore Runtime. | `string` | `"finance_helper"` | no |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region to deploy resources into. | `string` | `"us-east-1"` | no |
| <a name="input_ecr_repository_name"></a> [ecr\_repository\_name](#input\_ecr\_repository\_name) | Name of the ECR repository for the finance-helper container image. | `string` | `"agentcore-finance-helper"` | no |
| <a name="input_image_tag"></a> [image\_tag](#input\_image\_tag) | Docker image tag to deploy to AgentCore Runtime. | `string` | `"latest"` | no |
| <a name="input_memory_event_expiry_days"></a> [memory\_event\_expiry\_days](#input\_memory\_event\_expiry\_days) | How long AgentCore Memory retains conversation events (days). | `number` | `90` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_agent_runtime_arn"></a> [agent\_runtime\_arn](#output\_agent\_runtime\_arn) | AgentCore Runtime ARN. |
| <a name="output_agent_runtime_id"></a> [agent\_runtime\_id](#output\_agent\_runtime\_id) | AgentCore Runtime ID (use with the AWS CLI to invoke the runtime). |
| <a name="output_ecr_repository_url"></a> [ecr\_repository\_url](#output\_ecr\_repository\_url) | ECR repository URL for the finance-helper image. |
| <a name="output_memory_id"></a> [memory\_id](#output\_memory\_id) | AgentCore Memory ID for conversation history. |
<!-- END_TF_DOCS -->
