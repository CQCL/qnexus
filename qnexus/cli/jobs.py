import click


# Job commands
@click.command()
def list():
    """List jobs/"""
    click.echo("Listing jobs...")


@click.command()
def create():
    """Submit a job"""
    click.echo("Created job...")


# Create jobs interface
@click.group()
def jobs():
    """Jobs interface"""


jobs.add_command(list)
jobs.add_command(create)
