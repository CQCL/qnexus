"""CLI for qnexus."""

import click

from ..client import auth as _auth


@click.command()
def login() -> None:
    """Log in to quantinuum nexus using your web browser."""
    click.echo(_auth.login())  # type: ignore[func-returns-value]


@click.command()
def logout() -> None:
    """Log out of quantinuum nexus."""
    click.echo(_auth.logout())  # type: ignore[func-returns-value]
