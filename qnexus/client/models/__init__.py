"""Models for use by the client."""

from typing import Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel

from qnexus.client.models.annotations import Annotations
from qnexus.client.models.backend_config import (
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
from qnexus.client.models.backend_info import StoredBackendInfo
from qnexus.client.models.utils import assert_never
from qnexus.references import TeamRef, UserRef

__all__ = [
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
    "StoredBackendInfo",
]


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
    """A role for use in RBAC assignments."""

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


class RoleInfo(BaseModel):
    """Information on a role assigned on a resource."""

    assignment_type: Literal["user", "team", "public"]
    assignee: TeamRef | UserRef | None
    role: Role

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""

        assignee_name: str | None = None
        match self.assignee:
            case TeamRef():
                assignee_name = self.assignee.name
            case UserRef():
                assignee_name = self.assignee.email
            case None:
                assignee_name = None
            case _:
                assert_never(self.assignee)

        return pd.DataFrame(
            {
                "assignment_type": self.assignment_type,
                "assignee": assignee_name,
                "role": self.role.name,
            },
            index=[0],
        )


class Property(BaseModel):
    """A property definition."""

    annotations: Annotations
    property_type: str
    required: bool
    color: str
    id: UUID

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "property_type": self.property_type,
                    "required": self.required,
                    "color": self.color,
                },
                index=[0],
            )
        )
