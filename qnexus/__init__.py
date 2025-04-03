"""The qnexus package."""

import nest_asyncio  # type: ignore

from qnexus import context, filesystem
from qnexus.client import (
    auth,
    circuits,
    credentials,
    devices,
    hugr,
    jobs,
    projects,
    quotas,
    roles,
    teams,
    users,
    wasm_modules,
)
from qnexus.client.auth import login, login_with_credentials, logout
from qnexus.client.jobs import compile, execute
from qnexus.client.jobs._compile import start_compile_job
from qnexus.client.jobs._execute import start_execute_job
from qnexus.models import (
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
    "credentials",
    "devices",
    "hugr",
    "jobs",
    "projects",
    "quotas",
    "teams",
    "compile",
    "execute",
    "users",
    "wasm_modules",
    "filesystem",
    "start_compile_job",
    "start_execute_job",
    "login",
    "login_with_credentials",
    "logout",
    "AerConfig",
    "AerStateConfig",
    "AerUnitaryConfig",
    "BackendConfig",
    "BraketConfig",
    "IBMQConfig",
    "IBMQEmulatorConfig",
    "ProjectQConfig",
    "QuantinuumConfig",
    "QulacsConfig",
]
