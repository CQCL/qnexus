"""The qnexus package."""
# pylint: disable=useless-import-alias, redefined-builtin

import nest_asyncio  # type: ignore

from qnexus import context
from qnexus.client import (
    assignment,
    auth,
    circuit,
    credential,
    device,
    job,
    project,
    quota,
    team,
    user,
)
from qnexus.client.job import compile, execute
from qnexus.client.job._compile import start_compile_job
from qnexus.client.job._execute import start_execute_job
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
    "assignment",
    "auth",
    "circuit",
    "device",
    "job",
    "project",
    "quota",
    "team",
    "compile",
    "execute",
]
