"""CLI for qnexus."""
import click
from typing_extensions import Unpack

from qnexus.client.job import Params, ParamsDict
from qnexus.client.job import get
from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get)
def jobs(**kwargs: Unpack[ParamsDict]):
    """List jobs."""
    click.echo(get(**kwargs))


add_options_to_command(jobs, Params)
