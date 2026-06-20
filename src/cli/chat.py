import json
import os
import urllib.parse
import uuid
from typing import Optional

import boto3
import httpx
import typer
from botocore.auth import SigV4Auth as _BotocoreSigV4
from botocore.awsrequest import AWSRequest as _AWSRequest

from cli.tokens import get_config

_AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def chat(
    session: Optional[str] = typer.Option(
        None, help="Resume a previous conversation by session ID."
    ),
):
    """Start an interactive chat session."""
    config = get_config()
    session_id = session or str(uuid.uuid4())

    typer.echo(f"Session: {session_id}")
    typer.echo("Type a message and press Enter. Ctrl-C to quit.\n")

    _run_chat_loop(config, session_id)


def _invoke(runtime_arn: str, session_id: str, prompt: str) -> str:
    encoded_arn = urllib.parse.quote(runtime_arn, safe="")
    url = f"https://bedrock-agentcore.{_AWS_REGION}.amazonaws.com/runtimes/{encoded_arn}/invocations"
    body = json.dumps({"prompt": prompt}).encode()

    creds = boto3.Session().get_credentials().get_frozen_credentials()
    aws_req = _AWSRequest(
        method="POST",
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
        },
    )
    _BotocoreSigV4(creds, "bedrock-agentcore", _AWS_REGION).add_auth(aws_req)
    response = httpx.post(url, headers=dict(aws_req.headers), content=body, timeout=60)
    response.raise_for_status()
    return response.json().get("response", "")


def _run_chat_loop(config: dict, session_id: str) -> None:
    while True:
        try:
            prompt = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not prompt.strip():
            continue

        try:
            response_text = _invoke(config["runtime_arn"], session_id, prompt)
            typer.echo(f"Agent: {response_text}\n")
        except httpx.HTTPStatusError as e:
            typer.echo(f"Error {e.response.status_code}: {e.response.text}", err=True)
            break
