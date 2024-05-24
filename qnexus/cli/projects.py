"""CLI for qnexus."""

import click
from typing_extensions import Unpack

from qnexus.client.project import Params, ParamsDict
from qnexus.client.project import get

from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get)
def projects(**kwargs: Unpack[ParamsDict]):
    """List all projects"""
    click.echo(get(**kwargs))


add_options_to_command(projects, Params)
