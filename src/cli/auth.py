import boto3
import typer

auth_app = typer.Typer(help="Authentication commands.", invoke_without_command=True)


@auth_app.callback()
def auth_default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        _show_identity()


def _show_identity() -> None:
    try:
        identity = boto3.client("sts").get_caller_identity()
        typer.echo(f"AWS Account: {identity['Account']}")
        typer.echo(f"Identity:    {identity['Arn']}")
    except Exception as e:
        typer.echo(f"No valid AWS credentials found: {e}", err=True)
        raise typer.Exit(code=1)


@auth_app.command()
def status():
    """Show current AWS identity."""
    _show_identity()
