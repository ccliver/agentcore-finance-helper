# agentcore-finance-helper

An AI-powered financial assistant built on [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/). Ask natural-language questions about compound interest, loan payments, savings growth, and investment projections. Conversations are stateful — the agent remembers context within a session and across sessions via AgentCore Memory.

Authentication uses **AWS IAM** (SigV4 signing) throughout — no separate identity provider required.

---

## Architecture

```
finance-helper CLI
     │ SigV4
     ▼
AgentCore Runtime (ECS container)
     │ SigV4
     ▼
AgentCore Gateway (MCP)
     │ IAM role
     ▼
AWS Lambda  ←  compound_interest, loan_payment tools
```

- **Agent**: [Strands Agents](https://github.com/strands-ai/strands-agents) + Claude Haiku 4.5 via Amazon Bedrock
- **Runtime**: Containerized on AWS Bedrock AgentCore Runtime, pulled from ECR
- **Gateway**: AgentCore Gateway (MCP protocol) proxies tool calls to Lambda; `AWS_IAM` authorizer
- **Tools**: `compound_interest` and `loan_payment` run in a single Lambda function; tool schemas are declared in Terraform
- **Memory**: AgentCore Memory for multi-turn conversation history, ID stored in SSM Parameter Store
- **Auth**: AWS IAM — SigV4 signed requests from CLI → Runtime and Runtime → Gateway
- **Infrastructure**: Terraform (AWS provider `>= 6.21`)

---

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) configured with a profile named `lab`
- [Terraform](https://developer.hashicorp.com/terraform) >= 1.0
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://www.docker.com/) with `buildx` for `linux/arm64`
- [Task](https://taskfile.dev/) (`brew install go-task`)

---

## Deploy

```bash
task deploy     # init Terraform, create ECR, push image, apply all infrastructure
task install    # install the finance-helper CLI locally via uv
```

---

## Usage

```bash
# Check AWS identity
finance-helper auth

# Start a chat session
finance-helper chat

# Resume a previous session
finance-helper chat --session <uuid>
```

**Example session:**

```
Session: 3f2a1b4c-...
Type a message and press Enter. Ctrl-C to quit.

You: If I invest $5000 at 7% for 20 years with $200/month, what do I end up with?
Agent: With a $5,000 initial investment at 7% annual interest compounded monthly,
       adding $200 each month for 20 years, you'd end up with approximately $112,843.
       You contributed $53,000 total and earned $59,843 in interest.

You: What would my monthly payment be on a $300k mortgage at 6.5% for 30 years?
Agent: Your monthly payment would be approximately $1,896. Over 30 years you'd pay
       $382,560 total — $82,560 in interest on top of the $300,000 principal.
```

---

## Adding or Updating Tools

Tools are Lambda functions with schemas declared in `terraform/gateway.tf`. To add a tool:

1. Add the function to `src/tools/lambda_handler.py` and register it in `TOOLS`
2. Add an `aws_bedrockagentcore_gateway_target` block in `terraform/gateway.tf`
3. Run `terraform apply` — no container rebuild needed

---

## Development

```bash
task test    # run pytest
task lint    # ruff + pre-commit checks
task build   # build Docker image locally (linux/arm64)
task apply   # apply Terraform changes without rebuilding the container
```

---

## Teardown

```bash
task destroy    # destroys all AWS infrastructure (prompts for confirmation)
```
