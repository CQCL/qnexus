import click
from .utils import add_options_to_command, is_documented_by
from ..client.jobs import jobs as _jobs, ParamsDict, Params
from typing_extensions import Unpack


@click.command()
@is_documented_by(_jobs)
def jobs(**kwargs: Unpack[ParamsDict]):
    """List jobs."""
    click.echo(_jobs(**kwargs))
    pass


add_options_to_command(jobs, Params)
