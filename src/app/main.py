import functools
import os

import boto3
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
_MEMORY_SSM_PARAM = "/agentcore-finance-helper/memory-id"

model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name=AWS_REGION,
)


@tool
def compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12,
    additional_monthly: float = 0.0,
) -> dict:
    """Calculate compound interest and return the final balance and total interest earned.

    Args:
        principal: Initial investment amount in dollars.
        annual_rate: Annual interest rate as a percentage (e.g. 5 for 5%).
        years: Number of years to compound.
        compounds_per_year: How many times interest compounds per year (default 12 for monthly).
        additional_monthly: Optional fixed amount added each month (default 0). Use this to
            model regular contributions such as monthly savings deposits.
    """
    rate = annual_rate / 100
    n = compounds_per_year

    principal_balance = principal * (1 + rate / n) ** (n * years)

    contributions_balance = 0.0
    if additional_monthly:
        monthly_rate = (1 + rate / n) ** (n / 12) - 1
        months = years * 12
        if monthly_rate:
            contributions_balance = additional_monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)
        else:
            contributions_balance = additional_monthly * months

    final_balance = principal_balance + contributions_balance
    total_contributed = principal + additional_monthly * 12 * years

    return {
        "final_balance": round(final_balance, 2),
        "total_interest": round(final_balance - total_contributed, 2),
        "principal": principal,
        "total_contributed": round(total_contributed, 2),
        "years": years,
    }


@functools.lru_cache(maxsize=1)
def _get_memory_id() -> str:
    memory_id = os.getenv("MEMORY_ID")
    if memory_id:
        return memory_id
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    return ssm.get_parameter(Name=_MEMORY_SSM_PARAM)["Parameter"]["Value"]


@app.entrypoint
def invoke(payload, context: BedrockAgentCoreContext):
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=AgentCoreMemoryConfig(
            memory_id=_get_memory_id(),
            session_id=context.session_id,
            actor_id=payload.get("actor_id", "default"),
        ),
        region_name=AWS_REGION,
    )
    agent = Agent(model=model, session_manager=session_manager, tools=[compound_interest])
    result = agent(payload.get("prompt", ""))
    return {"response": str(result)}


if __name__ == "__main__":
    app.run()
