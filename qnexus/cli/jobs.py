"""CLI for qnexus."""

from typing import Any

import click

from qnexus.client.jobs import Params, get_all

from .utils import add_options_to_command, is_documented_by


@click.command()
@is_documented_by(get_all)
def jobs(**kwargs: Any) -> None:
    """List jobs."""
    click.echo(get_all(**kwargs))


add_options_to_command(jobs, Params)
