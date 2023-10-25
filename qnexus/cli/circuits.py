import click


# Job commands
@click.command()
def list():
    """List all circuits in this project."""
    click.echo("Listing circuits...")


@click.command()
def create():
    """Upload a circuit to Nexus."""
    click.echo("Creating circuit...")


@click.command()
def delete():
    """Delete a circuit."""
    click.echo("Deleting circuit...")


@click.command()
def edit():
    """Modify an already uploaded circuit."""
    click.echo("Modifying circuit...")


# Create circuits interface
@click.group()
def circuits():
    """List, create & delete circuits."""


circuits.add_command(list)
circuits.add_command(create)
circuits.add_command(delete)
circuits.add_command(edit)
