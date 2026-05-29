import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import click
import httpx

from cli.tokens import TokenStore, generate_pkce_pair, get_config


@click.group()
def auth():
    """Authentication commands."""


@auth.command()
def login():
    """Log in with your Microsoft account (opens browser)."""
    config = get_config()
    store = TokenStore()

    code_verifier, code_challenge = generate_pkce_pair()
    port = config["callback_port"]
    result = {"code": None, "error": None}
    server_holder = [None]

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            if "code" in params:
                result["code"] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Login successful! You can close this tab.</h2></body></html>"
                )
            else:
                result["error"] = params.get(
                    "error_description", params.get("error", ["Unknown error"])
                )[0]
                self.send_response(400)
                self.end_headers()

            threading.Thread(target=server_holder[0].shutdown, daemon=True).start()

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("localhost", port), CallbackHandler)
    server_holder[0] = server

    auth_url = (
        f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/authorize"
        f"?response_type=code"
        f"&client_id={config['client_id']}"
        f"&redirect_uri={urllib.parse.quote(f'http://localhost:{port}/callback', safe='')}"
        f"&scope=openid+email+profile+offline_access"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )

    click.echo("Opening browser for authentication...")
    click.launch(auth_url)
    server.serve_forever()

    if result["error"]:
        click.echo(f"Login failed: {result['error']}", err=True)
        sys.exit(1)

    response = httpx.post(
        f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/token",
        data={
            "grant_type": "authorization_code",
            "client_id": config["client_id"],
            "code": result["code"],
            "redirect_uri": f"http://localhost:{port}/callback",
            "code_verifier": code_verifier,
        },
    )
    response.raise_for_status()
    store.save(response.json())
    click.echo(f"Logged in as {store.email()}")


@auth.command()
def logout():
    """Clear stored credentials."""
    TokenStore().clear()
    click.echo("Logged out.")


@auth.command()
def status():
    """Show current authentication status."""
    import time

    store = TokenStore()
    tokens = store.load()
    if not tokens:
        click.echo("Not logged in.")
        return

    expires_in = int(tokens["expires_at"] - time.time())
    if expires_in < 0:
        click.echo(
            f"Session expired ({store.email()}). Run `finance-helper auth login`."
        )
    else:
        click.echo(
            f"Logged in as {store.email()} (token expires in {expires_in // 60}m)"
        )
