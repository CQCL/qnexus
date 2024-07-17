"""The qnexus package."""
# pylint: disable=useless-import-alias, redefined-builtin

import nest_asyncio  # type: ignore

from qnexus import context
from qnexus.client import (
    auth,
    circuits,
    credentials,
    devices,
    jobs,
    projects,
    quotas,
    roles,
    teams,
    users,
)
from qnexus.client.auth import login, login_with_credentials, logout
from qnexus.client.jobs import compile, execute
from qnexus.client.jobs._compile import start_compile_job
from qnexus.client.jobs._execute import start_execute_job
from qnexus.client.models import (
    AerConfig,
    AerStateConfig,
    AerUnitaryConfig,
    BackendConfig,
    BraketConfig,
    IBMQConfig,
    IBMQEmulatorConfig,
    ProjectQConfig,
    QuantinuumConfig,
    QulacsConfig,
)

# This is necessary for use in Jupyter notebooks to allow for nested asyncio loops
try:
    nest_asyncio.apply()
except (RuntimeError, ValueError):
    # May fail in some cloud environments: ignore.
    pass

__all__ = [
    "context",
    "roles",
    "auth",
    "circuits",
    "devices",
    "jobs",
    "projects",
    "quotas",
    "teams",
    "compile",
    "execute",
    "login",
    "login_with_credentials",
    "logout",
]
