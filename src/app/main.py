import functools
import os

import boto3
import httpx
from botocore.auth import SigV4Auth as _BotocoreSigV4
from botocore.awsrequest import AWSRequest as _AWSRequest
from bedrock_agentcore import BedrockAgentCoreApp, BedrockAgentCoreContext
from bedrock_agentcore.memory.integrations.strands.session_manager import (
    AgentCoreMemorySessionManager,
)
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

app = BedrockAgentCoreApp()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
GATEWAY_URL = os.getenv("GATEWAY_URL", "")
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
)
_MEMORY_SSM_PARAM = "/agentcore-finance-helper/memory-id"

model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    region_name=AWS_REGION,
)


class _GatewaySigV4(httpx.Auth):
    requires_request_body = True

    def auth_flow(self, request: httpx.Request):
        creds = boto3.Session().get_credentials().get_frozen_credentials()
        aws_req = _AWSRequest(
            method=request.method,
            url=str(request.url),
            data=request.content,
            headers=dict(request.headers),
        )
        _BotocoreSigV4(creds, "bedrock-agentcore", AWS_REGION).add_auth(aws_req)
        request.headers.update(dict(aws_req.headers))
        yield request


@functools.lru_cache(maxsize=1)
def _get_memory_id() -> str:
    memory_id = os.getenv("MEMORY_ID")
    if memory_id:
        return memory_id
    ssm = boto3.client("ssm", region_name=AWS_REGION)
    return ssm.get_parameter(Name=_MEMORY_SSM_PARAM)["Parameter"]["Value"]


@app.entrypoint
def invoke(payload, context: BedrockAgentCoreContext):
    try:
        session_manager = AgentCoreMemorySessionManager(
            agentcore_memory_config=AgentCoreMemoryConfig(
                memory_id=_get_memory_id(),
                session_id=context.session_id,
                actor_id=payload.get("actor_id", "default"),
            ),
            region_name=AWS_REGION,
        )
        mcp = MCPClient(
            lambda: streamable_http_client(
                GATEWAY_URL,
                http_client=create_mcp_http_client(auth=_GatewaySigV4()),
            )
        )
        agent = Agent(model=model, session_manager=session_manager, tools=[mcp])
        result = agent(payload.get("prompt", ""))
        return {"response": str(result)}
    except Exception:
        import traceback
        return {"response": f"ERROR: {traceback.format_exc()}"}


if __name__ == "__main__":
    app.run()
