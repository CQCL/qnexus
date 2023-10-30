import click
import os
from colorama import Fore
from ..consts import CONFIG_FILE_NAME
from ..config import get_config
from .. import client
from click import Option, Command
from typing import Any

current_path = os.getcwd()
current_dir = current_path.split(os.sep)[-1]


# QNX utils interface
@click.command()
def status():
    """Print a short summary of the current project."""
    # click.echo(client.status())
    click.echo("A brief summary of the current project.")


@click.command()
def init():
    """Initialize a new qnexus project."""
    # A project with that name already exists, use that one?
    config = get_config()
    if config:
        raise click.ClickException(
            Fore.GREEN
            + f"Project already initialized: {Fore.YELLOW + config.project_name}"
        )
    if config is None:
        name: str = click.prompt(
            "Enter a project name:",
            default=current_dir,
        )
        click.echo(Fore.GREEN + f"Intialized qnexus project: {name}")


def add_options_to_command(command: Command, model: Any):
    # Annotate command with options from dict
    for field, value in model.model_fields.items():
        command.params.append(
            Option(
                [f"--{field}"],
                help=value.description,
                show_default=True,
                default=value.default,
                type=value.annotation,
            )
        )
