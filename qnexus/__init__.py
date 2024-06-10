"""The qnexus package."""
# pylint: disable=useless-import-alias, redefined-builtin

import nest_asyncio  # type: ignore

from qnexus import context
from qnexus.client import (
    assignment,
    auth,
    circuit,
    device,
    job,
    project,
    quota,
    team,
    user,
)
from qnexus.client.job.compile import _compile as compile
from qnexus.client.job.execute import _execute as execute
from qnexus.client.models.nexus_dataclasses import (
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
