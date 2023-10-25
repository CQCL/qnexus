import click


# Job commands
@click.command()
def list():
    """List circuits"""
    click.echo("Listing circuits...")


@click.command()
def create():
    """Submit a job"""
    click.echo("Created circuit...")


# Create circuits interface
@click.group()
def circuits():
    """Circuits interface"""


circuits.add_command(list)
circuits.add_command(create)
