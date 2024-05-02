"""Definitions of reference proxy objects to data in Nexus."""

# pylint: disable=import-outside-toplevel, too-few-public-methods, cyclic-import
from __future__ import annotations

from abc import abstractmethod
from copy import copy
from enum import Enum
from typing import Optional, Protocol, TypeVar
from uuid import UUID

import pandas as pd
from pydantic import BaseModel, ConfigDict
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum
from pytket.circuit import Circuit

from qnexus.client.models.annotations import Annotations


class Dataframable(Protocol):
    """Protocol for structural subtyping of classes that
    have a default representation as a pandas.DataFrame."""

    @abstractmethod
    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        raise NotImplementedError


T = TypeVar("T", bound=Dataframable)


class DataframableList(list[T]):
    """A Python list that implements the Dataframable protocol."""

    def __init__(self, iterable):
        super().__init__(item for item in iterable)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        # TODO handle mixed types (e.g. None and float) - found in quotas
        return pd.concat([item.df() for item in self], ignore_index=True)


class BaseRef(BaseModel):
    """Base pydantic model."""

    model_config = ConfigDict(frozen=True)


class TeamsRef(BaseRef):
    """Proxy object to a Team in Nexus."""

    name: str
    description: Optional[str]
    id: UUID

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.name,
                "description": self.description,
                "id": self.id,
            },
            index=[0],
        )


class ProjectRef(BaseRef):
    """Proxy object to a Project in Nexus."""

    annotations: Annotations
    id: UUID

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "id": self.id,
                },
                index=[0],
            )
        )


class CircuitRef(BaseRef):
    """Proxy object to a Circuit in Nexus."""

    annotations: Annotations
    project: ProjectRef
    id: UUID
    _circuit: Circuit | None = None

    def get_circuit(self) -> Circuit:  # TODO
        """Get a copy of the pytket circuit."""
        if self._circuit:
            return self._circuit.copy()
        from qnexus.client.circuit import _fetch_circuit

        self._circuit = _fetch_circuit(self)
        return self._circuit.copy()

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "project": self.project.annotations.name,
                    "id": self.id,
                },
                index=[0],
            )
        )


class JobType(str, Enum):
    """Enum for a job's type."""

    EXECUTE = "PROCESS"
    COMPILE = "COMPILE"


class JobRef(BaseRef):
    """Proxy object to a Circuit in Nexus."""

    model_config = ConfigDict(frozen=False)

    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef
    id: UUID

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "job_type": self.job_type,
                    "last_status": self.last_status,
                    "project": self.project.annotations.name,
                    "id": self.id,
                },
                index=[0],
            )
        )


class CompilationResultRef(BaseRef):
    """Proxy object to the results of a compilation in Nexus."""

    annotations: Annotations
    project: ProjectRef
    _compiled_circuit: CircuitRef | None = None
    _compilation_passes: DataframableList | None = (
        None  # RefList[tuple[str, CircuitRef]]
    )
    id: UUID  # compilation id

    def get_compiled_circuit(self) -> CircuitRef:
        """Get a copy of the compiled pytket circuit."""
        # TODO check naming of this - its a ref so its confusing
        if self._compiled_circuit:
            return self._compiled_circuit

        from qnexus.client.job.compile import _fetch_compilation_passes

        self._compilation_passes = _fetch_compilation_passes(self)
        self._compiled_circuit = self._compilation_passes[-1].circuit
        return self._compiled_circuit

    def get_compilation_passes(self) -> DataframableList[CompilationPassRef]:
        """Get information on the compilation passes and the output circuits."""
        # TODO is this copy actually helpful?
        if self._compilation_passes:
            return copy(self._compilation_passes)

        from qnexus.client.job.compile import _fetch_compilation_passes

        self._compilation_passes = _fetch_compilation_passes(self)
        self._compiled_circuit = self._compilation_passes[-1].circuit
        return copy(self._compilation_passes)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "project": self.project.annotations.name,
                    "id": self.id,
                },
                index=[0],
            )
        )


class ExecutionResultRef(BaseRef):
    """Proxy object to the results of a circuit execution through Nexus."""

    annotations: Annotations
    project: ProjectRef
    _backend_result: BackendResult | None = None
    _backend_info: BackendInfo | None = None
    id: UUID

    def get_backend_result(self) -> BackendResult:
        """Get a copy of the pytket BackendResult."""
        if self._backend_result:
            return copy(self._backend_result)
        from qnexus.client.job.execute import _fetch_execution_result

        self._backend_result, self._backend_info = _fetch_execution_result(self)
        return copy(self._backend_result)

    def get_backend_info(self) -> BackendInfo:
        """Get a copy of the pytket BackendInfo."""
        if self._backend_info:
            return copy(self._backend_info)
        from qnexus.client.job.execute import _fetch_execution_result

        self._backend_result, self._backend_info = _fetch_execution_result(self)
        return copy(self._backend_info)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "project": self.project.annotations.name,
                    "id": self.id,
                },
                index=[0],
            )
        )


class CompilationPassRef(BaseModel):
    """Proxy object to a compilation pass that was applied on a circuit in Nexus."""

    pass_name: str
    circuit: CircuitRef
    id: UUID

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return (
            pd.DataFrame({"pass name": self.pass_name}, index=[0])
            .join(self.circuit.df())
            .join(other=pd.DataFrame({"id": self.id}, index=[0]))
        )
