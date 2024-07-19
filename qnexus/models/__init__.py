"""Models for use by the client."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator
from pytket.backends.backendinfo import BackendInfo

from qnexus.models.annotations import Annotations
from qnexus.models.backend_config import (
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
from qnexus.models.backend_info import StoredBackendInfo
from qnexus.models.references import TeamRef, UserRef
from qnexus.models.utils import assert_never

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


class CredentialIssuer(str, Enum):
    """An Issuer of credentials."""

    QUANTINUUM = "Quantinuum"
    QISKIT = "Qiskit"
    BRAKET = "Braket"


class Credential(BaseModel):
    """A saved credential for a backend provider/issuer."""

    name: str
    backend_issuer: CredentialIssuer
    is_default_for_issuer: bool
    submitted_time: datetime
    id: str

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.name,
                "issuer": self.backend_issuer,
                "is_default_for_issuer": self.is_default_for_issuer,
                "created": self.submitted_time,
                "id": self.id,
            },
            index=[0],
        )


class Device(BaseModel):
    """A device in Nexus, work-in-progress"""

    backend_name: str
    device_name: Optional[str]
    nexus_hosted: bool
    backend_info: BackendInfo

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "backend_name": self.backend_name,
                "device_name": self.device_name,
                "nexus_hosted": self.nexus_hosted,
                "backend_info": self.backend_info.to_dict(),
            },
            index=[0],
        )

    @field_validator("backend_name")
    @classmethod
    def convert_backend_name(cls, v: str) -> str:
        """Convert the internal name for QuantinuumBackend."""
        if v == "EmulatorEnabledQuantinuumBackend":
            return "QuantinuumBackend"
        return v


class Quota(BaseModel):
    """A quota in Nexus."""

    name: str
    description: str
    usage: float
    quota: float | str

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
                assignee_name = self.assignee.display_name
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


class IssuerEnum(str, Enum):
    """Backend issuers in Nexus."""

    QUANTINUUM = "QUANTINUUM"
    IBMQ = "IBMQ"
    QISKIT = "QISKIT"
    BRAKET = "BRAKET"
    PROJECTQ = "PROJECTQ"
    QULACS = "QULACS"


def issuer_enum_to_config_str(issuer: IssuerEnum) -> list[str]:
    """Convert an IssuerEnum to a list of BackendConfig names."""

    match issuer:
        case IssuerEnum.QUANTINUUM:
            return ["QuantinuumConfig"]
        case IssuerEnum.IBMQ:
            return ["IBMQConfig"]
        case IssuerEnum.QISKIT:
            return [
                "IBMQEmulatorConfig",
                "AerConfig",
                "AerStateConfig",
                "AerUnitaryConfig",
            ]
        case IssuerEnum.PROJECTQ:
            return ["ProjectQConfig"]
        case IssuerEnum.QULACS:
            return ["QulacsConfig"]
        case IssuerEnum.BRAKET:
            return ["BraketConfig"]
        case _:
            assert_never(issuer)
