"""CLI for qnexus."""

import os
from typing import Any, Callable

from click import Command, Option

# from ..client import status as _status
from ..config import Config

config = Config()


def is_documented_by(original: Callable):
    """Forward the documentation from the underlying client function."""

    def wrapper(target: Callable):
        target.__doc__ = original.__doc__
        return target

    return wrapper


current_path = os.getcwd()
current_dir = current_path.split(os.sep)[-1]


# # QNX utils interface
# @click.command()
# @is_documented_by(_status)
# def status():
#     click.echo(_status())


# @click.command()
# def init():
#     """Initialize a new qnexus project."""
#     if config:
#         raise click.ClickException(
#             Fore.GREEN + f"Project already initialized: {Fore.YELLOW}"
#         )
#     if config is None:
#         name: str = click.prompt(
#             "Enter a project name:",
#             default=current_dir,
#         )
#         click.echo(Fore.GREEN + f"Intialized qnexus project: {name}")


def add_options_to_command(command: Command, model: Any):
    """Add click options using fields of a pydantic model."""
    # Annotate command with options from dict
    for field, value in model.model_fields.items():
        command.params.append(
            Option(
                [f"--{field}"],
                help=value.description,
                show_default=True,
                default=value.default,
                multiple=isinstance(value.default, list),
            )
        )
