import click
from ..client import auth as _auth


@click.command()
def login():
    """List all jobs"""
    click.echo(_auth.browser_login())
