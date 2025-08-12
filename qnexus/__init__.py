"""The qnexus package."""

import warnings

import nest_asyncio  # type: ignore
from quantinuum_schemas.models.backend_config import (
    AerConfig,
    AerStateConfig,
    AerUnitaryConfig,
    BackendConfig,
    BasicEmulatorConfig,
    BraketConfig,
    IBMQConfig,
    IBMQEmulatorConfig,
    ProjectQConfig,
    QuantinuumConfig,
    QulacsConfig,
    StandardEmulatorConfig,
)

import qnexus.models as models
from qnexus import context, filesystem
from qnexus.client import (
    auth,
    circuits,
    credentials,
    devices,
    gpu_decoder_configs,
    hugr,
    jobs,
    projects,
    qir,
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

warnings.filterwarnings("default", category=DeprecationWarning, module=__name__)

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
    "qir",
    "jobs",
    "projects",
    "quotas",
    "teams",
    "compile",
    "execute",
    "users",
    "wasm_modules",
    "gpu_decoder_configs",
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
    "BasicEmulatorConfig",
    "BraketConfig",
    "IBMQConfig",
    "IBMQEmulatorConfig",
    "ProjectQConfig",
    "QuantinuumConfig",
    "QulacsConfig",
    "StandardEmulatorConfig",
    "models",
]
