import click
from typing_extensions import Unpack

from ..client.projects import Params, ParamsDict, filter
from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(filter)
def projects(**kwargs: Unpack[ParamsDict]):
    """List all projects"""
    click.echo(filter(**kwargs))


add_options_to_command(projects, Params)
