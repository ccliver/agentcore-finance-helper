import base64
import hashlib
import json
import os
import secrets
import time
from pathlib import Path

import boto3
import httpx

_CONFIG_DIR = Path.home() / ".config" / "finance-helper"
_CREDENTIALS_FILE = _CONFIG_DIR / "credentials.json"
_AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def generate_pkce_pair() -> tuple[str, str]:
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


class TokenStore:
    def load(self) -> dict | None:
        if not _CREDENTIALS_FILE.exists():
            return None
        return json.loads(_CREDENTIALS_FILE.read_text())

    def save(self, token_response: dict) -> None:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        expires_at = time.time() + token_response.get("expires_in", 3600)
        data = {
            "access_token": token_response["access_token"],
            "id_token": token_response["id_token"],
            "refresh_token": token_response.get("refresh_token"),
            "expires_at": expires_at,
        }
        _CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))
        _CREDENTIALS_FILE.chmod(0o600)

    def clear(self) -> None:
        if _CREDENTIALS_FILE.exists():
            _CREDENTIALS_FILE.unlink()

    def is_expired(self) -> bool:
        tokens = self.load()
        if not tokens:
            return True
        return time.time() >= tokens["expires_at"] - 60

    def email(self) -> str:
        tokens = self.load()
        if not tokens:
            return "unknown"
        # Decode the JWT payload without signature verification (we trust our own Cognito)
        payload_b64 = tokens["id_token"].split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("email", payload.get("sub", "unknown"))


def get_config() -> dict:
    ssm = boto3.client("ssm", region_name=_AWS_REGION)
    value = ssm.get_parameter(Name="/agentcore-finance-helper/cli-config")["Parameter"][
        "Value"
    ]
    return json.loads(value)


def refresh_tokens(store: TokenStore, config: dict) -> None:
    tokens = store.load()
    if not tokens or not tokens.get("refresh_token"):
        return
    response = httpx.post(
        f"{config['domain']}/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "client_id": config["client_id"],
            "refresh_token": tokens["refresh_token"],
        },
    )
    response.raise_for_status()
    store.save(response.json())
