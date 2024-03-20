import nest_asyncio

from qnexus.client import (
    assignments as assignments,
    projects as projects,
    auth as auth,
    jobs as jobs,
    circuits as circuits,
    quotas as quotas,
    teams as teams,
    devices as devices,
)
from qnexus import context


# This is necessary for use in Jupyter notebooks to allow for nested asyncio loops
try:
    nest_asyncio.apply()
except (RuntimeError, ValueError):
    # May fail in some cloud environments: ignore.
    pass