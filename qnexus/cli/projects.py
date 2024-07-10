"""CLI for qnexus."""

from typing import Any

import click

from qnexus.client.project import Params, get

from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get)
def projects(**kwargs: Any):
    """List all projects"""
    click.echo(get(**kwargs))


add_options_to_command(projects, Params)
