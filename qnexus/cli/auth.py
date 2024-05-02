"""CLI for qnexus."""
import click

from ..client import auth as _auth


@click.command()
def login():
    """Log in to quantinuum nexus using your web browser."""
    click.echo(_auth.login())


@click.command()
def logout():
    """Log out of quantinuum nexus."""
    click.echo(_auth.logout())
