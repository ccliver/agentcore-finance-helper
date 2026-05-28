import click

from cli.auth import auth
from cli.chat import chat


@click.group()
def cli():
    """Finance helper — AI-powered financial assistant."""


cli.add_command(auth)
cli.add_command(chat)
