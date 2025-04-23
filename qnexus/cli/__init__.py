"""CLI for qnexus."""

import click

from .auth import login, logout

# from .jobs import jobs
# from .projects import projects
# from .utils import init, status


@click.group()
def entrypoint() -> None:
    """Quantinuum Nexus API client."""


# entrypoint.add_command(init)
# entrypoint.add_command(status)
# entrypoint.add_command(projects)
# entrypoint.add_command(jobs)
entrypoint.add_command(login)
entrypoint.add_command(logout)
