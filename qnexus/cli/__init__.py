import click

from .jobs import jobs
from .circuits import circuits
from .utils import status


@click.group()
def entrypoint():
    """Entry point"""
    pass


entrypoint.add_command(jobs)
entrypoint.add_command(circuits)
entrypoint.add_command(status)
