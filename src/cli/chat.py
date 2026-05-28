import json
import os
import sys
import urllib.parse
import uuid

import click
import httpx

from cli.tokens import TokenStore, get_config, refresh_tokens

_AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


@click.command()
@click.option(
    "--session", default=None, help="Resume a previous conversation by session ID."
)
def chat(session):
    """Start an authenticated interactive chat session."""
    store = TokenStore()
    if not store.load():
        click.echo("Not logged in. Run `finance-helper auth login` first.", err=True)
        sys.exit(1)

    config = get_config()

    if store.is_expired():
        try:
            refresh_tokens(store, config)
        except Exception:
            click.echo(
                "Session expired and refresh failed. Run `finance-helper auth login`.",
                err=True,
            )
            sys.exit(1)

    tokens = store.load()
    session_id = session or str(uuid.uuid4())

    click.echo(f"Logged in as {store.email()}")
    click.echo(f"Session: {session_id}")
    click.echo("Type a message and press Enter. Ctrl-C to quit.\n")

    _run_chat_loop(config, tokens, session_id)


def _invoke(runtime_arn: str, session_id: str, id_token: str, prompt: str) -> str:
    # The custom_jwt_authorizer replaces SigV4 — the Cognito token IS the credential.
    # We POST directly to the data plane with Authorization: Bearer instead of using boto3.
    encoded_arn = urllib.parse.quote(runtime_arn, safe="")
    url = f"https://bedrock-agentcore.{_AWS_REGION}.amazonaws.com/runtimes/{encoded_arn}/invocations"

    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {id_token}",
            "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
            "Content-Type": "application/json",
        },
        content=json.dumps({"prompt": prompt}).encode(),
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def _run_chat_loop(config: dict, tokens: dict, session_id: str) -> None:
    while True:
        try:
            prompt = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not prompt.strip():
            continue

        try:
            response_text = _invoke(
                config["runtime_arn"], session_id, tokens["id_token"], prompt
            )
            click.echo(f"Agent: {response_text}\n")
        except httpx.HTTPStatusError as e:
            click.echo(f"Error {e.response.status_code}: {e.response.text}", err=True)
            break
