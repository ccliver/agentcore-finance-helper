import functools
import os

import boto3
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from strands import Agent
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
_MEMORY_SSM_PARAM = "/agentcore-finance-helper/memory-id"

model = BedrockModel(
    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    region_name=AWS_REGION,
)


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
    agent = Agent(model=model, session_manager=session_manager)
    result = agent(payload.get("prompt", ""))
    return {"response": str(result)}


if __name__ == "__main__":
    app.run()
