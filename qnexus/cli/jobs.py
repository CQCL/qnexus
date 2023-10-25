import click


# Job commands
@click.command()
def list():
    """List all jobs"""
    click.echo("Listing jobs...")
    return 5


@click.command()
def create():
    """Submit a job to Nexus."""
    click.echo("Creating job...")


# Create jobs interface
@click.group()
def jobs():
    """List, create & cancel jobs."""


jobs.add_command(list)
jobs.add_command(create)
