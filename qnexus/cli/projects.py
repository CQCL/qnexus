"""CLI for qnexus."""

from typing import Any

import click

from qnexus.client.projects import Params, get_all

from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get_all)
def projects(**kwargs: Any) -> None:
    """List all projects"""
    click.echo(get_all(**kwargs))


add_options_to_command(projects, Params)
