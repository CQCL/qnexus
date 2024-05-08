"""Constants used for the qnexus integration tests."""

from os import getenv

# For now you probably don't want to point at prod: the integration tests leave
# artifacts behind and don't clean up after themselves
NEXUS_HOST = getenv("NEXUS_HOST", "staging.myqos.com")

NEXUS_USER_EMAIL = getenv("NEXUS_QA_USER_EMAIL", default="")
NEXUS_USER_PASSWORD = getenv("NEXUS_QA_USER_PASSWORD", default="")

NEXUS_INTEGRATION_TEST = getenv("NEXUS_INTEGRATION_TEST", default="noCI")
