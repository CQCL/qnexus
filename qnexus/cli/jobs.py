"""CLI for qnexus."""
from typing import Any

import click

from qnexus.client.job import Params, get

from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get)
def jobs(**kwargs: Any):
    """List jobs."""
    click.echo(get(**kwargs))


add_options_to_command(jobs, Params)
