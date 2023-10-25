"""Quantinuum Nexus API client."""

import os
from typing import Dict, Optional, Any, Annotated
from pathlib import Path
from functools import reduce

from pydantic import BaseModel, ConfigDict, ValidationError, BeforeValidator
from colorama import Fore
from .consts import CONFIG_FILE_NAME


class Config(BaseModel):
    """QNexus Configuration schema."""

    model_config = ConfigDict(coerce_numbers_to_str=True, extra="allow")
    project_name: Annotated[str, BeforeValidator(lambda v: None if v == "" else v)]
    optimization_level: Optional[int] = 1

    def __str__(self) -> str:
        out: str = ""
        out += Fore.MAGENTA + "Current QNexus Environment: \n"
        for key, field in self.model_fields.items():
            required = "(Required)" if field.is_required() else ""
            value = getattr(self, key).__str__()
            out += f"{Fore.CYAN + key} = {Fore.GREEN + value} {Fore.LIGHTBLUE_EX + required}\n"
        return out


def parse_config(path: str) -> Dict[str, Any]:
    """Read a config of key value pairs as a dict"""
    env_vars = {}
    with open(path, encoding="UTF-8") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            env_vars[name.strip()] = var.strip()
    return env_vars


def get_config_file_paths():
    """Get paths of all configuration files in the current tree."""

    cwd = os.path.dirname(__file__)
    config_files = []
    tree = Path(cwd).parents
    for directory_name in tree:
        config_path = f"{directory_name}/{CONFIG_FILE_NAME}"
        directory_has_config = os.path.isfile(config_path)
        if directory_has_config:
            config_files.append(config_path)
    return config_files


def get_config() -> Any:
    """Get config"""
    config_file_paths = get_config_file_paths()
    if len(config_file_paths) == 0:
        return None
        # print(
        #     Fore.LIGHTYELLOW_EX
        #     + f"No {CONFIG_FILE_NAME} file found in this directory or any of the parent directories. Please create a {CONFIG_FILE_NAME} file to initialize a project. "
        # )
        # return
    configs = [parse_config(config) for config in config_file_paths]
    configs.reverse()  # Nearest directory takes precendence
    return reduce(lambda a, b: dict(a, **b), configs)


def config():
    """Display the current QNX environment."""
    resolved_config = get_config()
    try:
        validated_config = Config(**resolved_config)
        print(validated_config)
        # pylint:disable=no-member
        extra = validated_config.__pydantic_extra__.items()
        if len(extra) > 0:
            print(Fore.YELLOW + "Unused environment variables:")
            for field_name, field in extra:
                print(field_name, "=", field)

    except ValidationError as e:
        print(Fore.RED + f"Required value missing in {CONFIG_FILE_NAME} file:")
        for err in e.errors():
            field_name = str(err.get("loc")[0])
            message = err.get("msg")
            value = getattr(err.get("input"), field_name, lambda: None)()
            print(
                Fore.RED + message,
                Fore.GREEN + field_name,
                f"with value: {value}" if value else "",
            )
