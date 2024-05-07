import click
from typing_extensions import Unpack

from qnexus.client.jobs import filter

from ..client.jobs import Params, ParamsDict
from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(filter)
def jobs(**kwargs: Unpack[ParamsDict]):
    """List jobs."""
    click.echo(filter(**kwargs))
    pass


add_options_to_command(jobs, Params)
