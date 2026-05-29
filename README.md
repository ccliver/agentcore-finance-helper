# agentcore-finance-helper

An AI-powered financial assistant built on [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/). Ask natural-language questions about compound interest, savings growth, and investment projections. Conversations are stateful — the agent remembers context within a session and across sessions via AgentCore Memory.

Authentication is handled by **Microsoft Entra ID** using a browser-based PKCE login flow, similar to `az login`.

---

## Architecture

```
finance-helper CLI  →  AgentCore Runtime (container)  →  Claude Haiku 4.5
      ↑ PKCE                  ↑ JWT auth                    ↑ compound_interest tool
  Entra ID             AgentCore Memory (SSM)
```

- **Agent**: [Strands Agents](https://github.com/strands-ai/strands-agents) + Claude Haiku 4.5 via Amazon Bedrock
- **Runtime**: Containerized on AWS Bedrock AgentCore Runtime, pulled from ECR
- **Memory**: AgentCore Memory for multi-turn conversation history
- **Auth**: Microsoft Entra ID — PKCE flow, JWT validation on the runtime
- **Infrastructure**: Terraform (AWS provider `>= 6.21`)

---

## Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) configured with a profile named `lab`
- [Terraform](https://developer.hashicorp.com/terraform) >= 1.0
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://www.docker.com/) with `buildx` for `linux/arm64`
- [Task](https://taskfile.dev/) (`brew install go-task`)
- A Microsoft Azure account with an Entra app registration (see below)

---

## One-time Entra Setup

1. Azure Portal → **Entra ID** → App registrations → **New registration**
   - Name: `finance-helper-cli`
   - Redirect URI: Platform = *Mobile and desktop applications*, URI = `http://localhost:9999/callback`
2. After creation: **Authentication** → enable **Allow public client flows**
3. Copy your **Directory (tenant) ID** and **Application (client) ID** into `terraform/terraform.tfvars`:

```hcl
entra_tenant_id = "<your-tenant-id>"
entra_client_id = "<your-client-id>"
```

---

## Deploy

```bash
task deploy     # init Terraform, create ECR, push image, apply all infrastructure
task install    # install the finance-helper CLI locally via uv
```

---

## Usage

```bash
# Authenticate (opens browser → Microsoft login)
finance-helper auth login

# Start a chat session
finance-helper chat

# Resume a previous session
finance-helper chat --session <uuid>

# Check auth status
finance-helper auth status

# Log out
finance-helper auth logout
```

**Example session:**

```
Session: 3f2a1b4c-...
Type a message and press Enter. Ctrl-C to quit.

You: If I invest $5000 at 7% for 20 years with $200/month, what do I end up with?
Agent: With a $5,000 initial investment at 7% annual interest compounded monthly,
       adding $200 each month for 20 years, you'd end up with approximately $112,843.
       You contributed $53,000 total and earned $59,843 in interest.
```

---

## Development

```bash
task test    # run pytest
task lint    # ruff + pre-commit checks
task build   # build Docker image locally (linux/arm64)
```

---

## Teardown

```bash
task destroy    # destroys all AWS infrastructure (prompts for confirmation)
```
