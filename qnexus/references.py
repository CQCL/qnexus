from abc import abstractmethod
from enum import Enum
from functools import cached_property
from uuid import UUID
from typing import Literal, Optional, Protocol, TypeVar

import pandas as pd
from pydantic import BaseModel, ConfigDict
from pytket.circuit import Circuit
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum

from qnexus.annotations import Annotations

T = TypeVar('T')


class RefList(list[T]):
    """ """
    def __init__(self, iterable):
        super().__init__(item for item in iterable)

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        # TODO handle mixed types (e.g. None and float) - found in quotas
        # TODO summarize utils/docs for extending default dataframes?
        return pd.concat([item.summarize() for item in self], ignore_index=True)


class Summarizable(Protocol):
    """Protocol for structural subtyping of classes that 
    have a default representation as a pandas.DataFrame."""

    @abstractmethod
    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        raise NotImplementedError


class BaseRef(BaseModel):
    model_config = ConfigDict(frozen=True)

class TeamsRef(BaseRef):

    name: str
    description: Optional[str]
    id: UUID

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return pd.DataFrame({
            "name": self.name,
            "description": self.description,
            "id": self.id,
        }, index=[0])


class ProjectRef(BaseRef):

    annotations: Annotations
    id: UUID

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return self.annotations.summarize().join(
            pd.DataFrame({
                "id": self.id,
            }, index=[0])
        )



class CircuitRef(BaseRef):

    annotations: Annotations
    project: ProjectRef
    id: UUID

    @cached_property
    def circuit(self) -> Circuit:
        from qnexus.client.circuits import _fetch_circuit
        return _fetch_circuit(self)

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return self.annotations.summarize().join(
            pd.DataFrame({
                "project": self.project.annotations.name,
                "id": self.id,
            }, index=[0])
        )

class JobType(str, Enum):
    Execute = "PROCESS"
    Compile = "COMPILE"


class JobRef(BaseRef):

    model_config = ConfigDict(frozen=False)

    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef
    id: UUID

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return self.annotations.summarize().join(
            pd.DataFrame({
            "job_type": self.job_type,
            "last_status": self.last_status,
            "project": self.project.annotations.name,
            "id": self.id,
        }, index=[0]))


class CompilationResultRef(BaseRef):

    annotations: Annotations
    project: ProjectRef
    _compiled_circuit: CircuitRef | None = None
    _compilation_passes: RefList | None = None # RefList[tuple[str, CircuitRef]]
    id: UUID # compilation id

    @property
    def compiled_circuit(self) -> CircuitRef:
        if self._compiled_circuit:
            return self._compiled_circuit

        from qnexus.client.jobs.compile import _fetch_compilation_passes
        self._compilation_passes = _fetch_compilation_passes(self) 
        self._compiled_circuit = self._compilation_passes[-1][1]
        return self._compiled_circuit


    @property
    def compilation_passes(self) -> RefList: # TODO typing
        """list of tuples of pass name and circuit."""
        if self._compilation_passes:
            return self._compilation_passes
        
        from qnexus.client.jobs.compile import _fetch_compilation_passes
        self._compilation_passes = _fetch_compilation_passes(self) 
        self._compiled_circuit = self._compilation_passes[-1][1]
        return self._compilation_passes

    
    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return self.annotations.summarize().join(
            pd.DataFrame({
                "project": self.project.annotations.name,
                "id": self.id,
            }, index=[0])
        )



class ExecutionResultRef(BaseRef):

    annotations: Annotations
    project: ProjectRef
    _backend_result: BackendResult | None = None
    _backend_info: BackendInfo | None = None
    id: UUID

    
    @property
    def backend_result(self) -> BackendResult:
        if self._backend_result:
            return self._backend_result
        from qnexus.client.jobs.execute import _fetch_execution_result
        self._backend_result, self._backend_info = _fetch_execution_result(self)
        return self._backend_result
    
    @property
    def backend_info(self) -> BackendInfo:
        if self._backend_info:
            return self._backend_info
        from qnexus.client.jobs.execute import _fetch_execution_result
        self._backend_result, self._backend_info = _fetch_execution_result(self)
        return self._backend_info
    
    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return self.annotations.summarize().join(
            pd.DataFrame({
                "project": self.project.annotations.name,
                "id": self.id,
            }, index=[0])
        )


class NexusRole(BaseModel):
    """ """
    id: UUID
    name: str
    description: str
    permissions: str #list[Permissions] - messes with pandas dataframe...
    type: Literal["role"] = "role"

    def summarize(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame({
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "id": self.id,
        }, index=[0])
    

class NexusQuota(BaseModel):
    # TODO move to Models?
    """ """
    name: str
    description: str
    usage: float
    quota: Optional[float]

    def summarize(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(self.model_dump(), index=[0])
    

class DeviceRef(BaseModel):
     # TODO move to Models?
    """ """
    backend_name: str
    device_name: Optional[str]
    nexus_hosted: bool

    def summarize(self) -> pd.DataFrame:
        """Summarize in a pandas DataFrame."""
        return pd.DataFrame(self.model_dump(), index=[0])