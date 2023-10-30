import click
from .utils import add_options_to_command
from ..client import projects as _projects
from typing_extensions import Unpack


@click.command()
def list_projects(**kwargs: Unpack[_projects.ParamsDict]):
    """List all projects"""
    click.echo(_projects.list_projects(**kwargs))


add_options_to_command(list_projects, _projects.Params)


@click.group()
def projects():
    """List, create & delete circuits."""
    pass


projects.add_command(list_projects, name="list")
