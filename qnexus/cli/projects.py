import click
from .utils import add_options_to_command, is_documented_by
from ..client.projects import projects as _projects, Params, ParamsDict
from typing_extensions import Unpack


@click.command()
@is_documented_by(_projects)
def projects(**kwargs: Unpack[ParamsDict]):
    """List all projects"""
    click.echo(_projects(**kwargs))


add_options_to_command(projects, Params)
