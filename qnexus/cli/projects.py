import click
from .utils import add_options_to_command
from ..client import projects as _projects
from typing_extensions import Unpack


@click.command()
def list(**kwargs: Unpack[_projects.ParamsDict]):
    """List all projects"""
    click.echo(_projects.list(**kwargs))


add_options_to_command(list, _projects.Params)


@click.group()
def projects():
    """List, create & delete circuits."""
    pass


projects.add_command(list)
