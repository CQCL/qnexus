"""Constants for use by the package."""

from os import getenv

CONFIG_FILE_NAME = ".env.qnx"
TOKEN_FILE_PATH = ".qnx/auth"
STORE_TOKENS = True

NEXUS_HOST = getenv("NEXUS_HOST", "nexus.quantinuum.com")
