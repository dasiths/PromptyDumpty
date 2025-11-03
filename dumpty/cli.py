"""CLI entry point for dumpty."""

import click
from dumpty import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Dumpty - Universal package manager for AI agent artifacts."""
    pass


@cli.command()
def hello():
    """Test command to verify installation."""
    click.echo("Hello from Dumpty!")


if __name__ == "__main__":
    cli()
