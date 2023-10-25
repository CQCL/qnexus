import click
import os
from colorama import Fore
from ..consts import CONFIG_FILE_NAME
from ..config import get_config

current_path = os.getcwd()
current_dir = current_path.split(os.sep)[-1]


# QNX utils interface
@click.command()
def status():
    """Utils"""
    click.echo("Current project")


@click.command()
def init():
    """Utils"""
    config = get_config()

    if config is None:
        name: str = click.prompt(
            "Enter a project name:",
            default=current_dir,
        )
        click.echo(Fore.GREEN + f"Intialized qnexus project: {name}")
