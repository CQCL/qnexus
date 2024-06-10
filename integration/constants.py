"""Constants used for the qnexus integration tests."""

from os import getenv

NEXUS_QA_USER_EMAIL = getenv("NEXUS_QA_USER_EMAIL", default="")
NEXUS_QA_USER_PASSWORD = getenv("NEXUS_QA_USER_PASSWORD", default="")
