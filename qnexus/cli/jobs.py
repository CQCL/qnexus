import click
from .utils import add_options_to_command
from ..client import jobs as _jobs
from typing_extensions import Unpack


@click.command()
def list_jobs(**kwargs: Unpack[_jobs.ParamsDict]):
    """List all jobs"""
    click.echo(_jobs.list_jobs(**kwargs))


add_options_to_command(list_jobs, _jobs.Params)


@click.group()
def jobs():
    """List jobs."""
    pass


jobs.add_command(list_jobs, name="list")
