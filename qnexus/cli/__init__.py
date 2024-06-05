"""CLI for qnexus."""

import click

from .auth import login, logout
from .circuits import circuits
from .jobs import jobs
from .projects import projects

<<<<<<< HEAD
# from .utils import init, status

=======
>>>>>>> 11eb4d1 (infra: remove old client CLI modules)

@click.group()
def entrypoint():
    """Quantinuum Nexus API client."""


<<<<<<< HEAD
# entrypoint.add_command(init)
entrypoint.add_command(circuits)
# entrypoint.add_command(status)
entrypoint.add_command(projects)
entrypoint.add_command(jobs)
=======
>>>>>>> 11eb4d1 (infra: remove old client CLI modules)
entrypoint.add_command(login)
entrypoint.add_command(logout)
