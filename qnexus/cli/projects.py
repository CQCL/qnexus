import click
from click import Option
from ..client import projects as _projects
from typing_extensions import Unpack


@click.command()
def list(**kwargs: Unpack[_projects.ParamsDict]):
    """List all projects"""
    click.echo(_projects.list(**kwargs))


# Annotate command with options from dict
for field, value in _projects.Params.model_fields.items():
    list.params.append(
        Option(
            [f"--{field}"],
            help=value.description,
            show_default=True,
            default=value.default,
            type=value.annotation,
        )
    )


@click.group()
def projects():
    """List, create & delete circuits."""
    pass


projects.add_command(list)
