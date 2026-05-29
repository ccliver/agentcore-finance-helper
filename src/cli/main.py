import typer

from cli.auth import auth_app
from cli.chat import chat

app = typer.Typer(help="Finance helper — AI-powered financial assistant.")
app.add_typer(auth_app, name="auth")
app.command()(chat)
