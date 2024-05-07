import nest_asyncio

from qnexus import context
from qnexus.client import (
    assignments as assignments,
    auth as auth,
    circuits as circuits,
    devices as devices,
    jobs as jobs,
    projects as projects,
    quotas as quotas,
    teams as teams,
)

# This is necessary for use in Jupyter notebooks to allow for nested asyncio loops
try:
    nest_asyncio.apply()
except (RuntimeError, ValueError):
    # May fail in some cloud environments: ignore.
    pass
