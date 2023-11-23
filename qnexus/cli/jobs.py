import click
from typing_extensions import Unpack

from ..client.jobs import Params, ParamsDict
from ..client.jobs import jobs as _jobs
from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(_jobs)
def jobs(**kwargs: Unpack[ParamsDict]):
    """List jobs."""
    click.echo(_jobs(**kwargs))
    pass


add_options_to_command(jobs, Params)
