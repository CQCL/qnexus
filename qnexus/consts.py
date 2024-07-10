"""Constants for use by the package."""

import os
from os import getenv


def str_to_bool(value: str) -> bool:
    """Convert an environment variable str to a bool."""
    return value.lower() in ("true", "1", "t", "y", "yes")


CONFIG_FILE_NAME = ".env.qnx"
TOKEN_FILE_PATH = os.environ.get("NEXUS_TOKEN_PATH") or ".qnx/auth"
STORE_TOKENS = str_to_bool(getenv("STORE_NEXUS_TOKENS", "true"))
NEXUS_HOST = getenv("NEXUS_HOST", "nexus.quantinuum.com")
