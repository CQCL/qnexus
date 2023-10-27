import click

from .jobs import jobs
from .circuits import circuits
from .utils import status, init
from ..config import get_config


@click.group()
def entrypoint():
    """Quantinuum Nexus API client."""
    get_config()  # Will raise an exception if the config is invalid.


entrypoint.add_command(init)
entrypoint.add_command(status)
entrypoint.add_command(jobs)
entrypoint.add_command(circuits)