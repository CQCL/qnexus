"""Models for use by the client."""

from typing import Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel


class Device(BaseModel):
    """A device in Nexus, work-in-progress"""

    backend_name: str
    device_name: Optional[str]
    nexus_hosted: bool

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(self.model_dump(), index=[0])


class Quota(BaseModel):
    """A quota in Nexus."""

    name: str
    description: str
    usage: float
    quota: Optional[float]

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(self.model_dump(), index=[0])


class Role(BaseModel):
    """An role for use in RBAC assignments."""

    id: UUID
    name: str
    description: str
    permissions: str
    type: Literal["role"] = "role"

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.name,
                "description": self.description,
                "permissions": self.permissions,
                "id": self.id,
            },
            index=[0],
        )
