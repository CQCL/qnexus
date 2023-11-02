import click

from .projects import projects
from .jobs import jobs
from .utils import status, init
from .auth import login, logout


@click.group()
def entrypoint():
    """Quantinuum Nexus API client."""


entrypoint.add_command(init)
entrypoint.add_command(status)
entrypoint.add_command(projects)
entrypoint.add_command(jobs)
entrypoint.add_command(login)
entrypoint.add_command(logout)
