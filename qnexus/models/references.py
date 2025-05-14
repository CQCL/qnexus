"""Definitions of reference proxy objects to data in Nexus."""

from __future__ import annotations

from abc import abstractmethod
from copy import copy
from datetime import datetime
from enum import Enum
from typing import (
    Annotated,
    Any,
    Iterable,
    Literal,
    Optional,
    Protocol,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

import pandas as pd
from hugr.package import Package
from hugr.qsystem.result import QsysResult
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum
from pytket.circuit import Circuit
from pytket.wasm.wasm import WasmModuleHandler
from quantinuum_schemas.models.backend_config import BackendConfig

from qnexus.models.annotations import Annotations
from qnexus.models.utils import assert_never


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

    def __init__(self, iterable: Iterable[T]) -> None:
        super().__init__(item for item in iterable)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        if len(self) == 0:
            return pd.DataFrame()
        return pd.concat([item.df() for item in self], ignore_index=True)


class BaseRef(BaseModel):
    """Base pydantic model."""

    model_config = ConfigDict(frozen=True)

    id: UUID


class TeamRef(BaseRef):
    """Proxy object to a Team in Nexus."""

    name: str
    description: Optional[str]
    id: UUID
    type: Literal["TeamRef"] = "TeamRef"

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


class UserRef(BaseRef):
    """Proxy object to a User in Nexus."""

    display_name: Optional[str]
    id: UUID
    type: Literal["UserRef"] = "UserRef"

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.display_name,
                "id": self.id,
            },
            index=[0],
        )


class ProjectRef(BaseRef):
    """Proxy object to a Project in Nexus."""

    annotations: Annotations
    contents_modified: datetime
    archived: bool = Field(default=False)
    id: UUID
    type: Literal["ProjectRef"] = "ProjectRef"

    @field_serializer("contents_modified")
    def serialize_modified(self, contents_modified: datetime | None) -> str | None:
        """Custom serializer for datetimes."""
        if contents_modified:
            return str(contents_modified)
        return None

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.annotations.name,
                "description": self.annotations.description,
                "created": self.annotations.created,
                "modified": self.annotations.modified,
                "contents_modified": self.contents_modified,
                "archived": self.archived,
                "id": self.id,
            },
            index=[0],
        )


class CircuitRef(BaseRef):
    """Proxy object to a Circuit in Nexus."""

    annotations: Annotations
    project: ProjectRef
    id: UUID
    _circuit: Circuit | None = None
    type: Literal["CircuitRef"] = "CircuitRef"

    def download_circuit(self) -> Circuit:
        """Get a copy of the circuit as a pytket ``Circuit`` object."""
        if self._circuit:
            return self._circuit.copy()
        from qnexus.client.circuits import _fetch_circuit

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


class WasmModuleRef(BaseRef):
    """Proxy object to a WasmModule in Nexus."""

    annotations: Annotations
    project: ProjectRef
    id: UUID
    _contents: WasmModuleHandler | None = None
    type: Literal["WasmModuleRef"] = "WasmModuleRef"

    def download_wasm_contents(self) -> WasmModuleHandler:
        """Get the contents of the original uploaded WASM."""
        if self._contents:
            return self._contents

        from qnexus.client.wasm_modules import _fetch_wasm_module

        self._contents = _fetch_wasm_module(self)
        return self._contents

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


class HUGRRef(BaseRef):
    """Proxy object to a HUGR in Nexus."""

    annotations: Annotations
    project: ProjectRef
    id: UUID
    _contents: Package | None = None
    type: Literal["HUGRRef"] = "HUGRRef"

    def download_hugr(self) -> Package:
        """Get the HUGR Package of the original uploaded HUGR."""

        if self._contents:
            return self._contents

        from qnexus.client.hugr import _fetch_hugr_package

        self._contents = _fetch_hugr_package(self)
        return self._contents

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

    EXECUTE = "execute"
    COMPILE = "compile"


class JobRef(BaseRef):
    """Proxy object to a Job in Nexus."""

    model_config = ConfigDict(frozen=False)

    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef
    id: UUID
    backend_config_store: BackendConfig | None = None
    type: Literal["JobRef", "CompileJobRef", "ExecuteJobRef"] = "JobRef"

    @property
    def backend_config(self) -> BackendConfig:
        """Fetch the backend_config for a job."""
        from qnexus.client.jobs import _fetch_by_id

        if self.backend_config_store:
            return self.backend_config_store
        self.backend_config_store = cast(
            BackendConfig, _fetch_by_id(self.id, None).backend_config_store
        )
        return self.backend_config_store

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "job_type": self.job_type,
                    "last_status": self.last_status,
                    "project": self.project.annotations.name,
                    "backend_config": self.backend_config.__class__.__name__,
                    "id": self.id,
                },
                index=[0],
            )
        )


class CompileJobRef(JobRef, BaseRef):
    """Proxy object to a CompileJob in Nexus."""

    model_config = ConfigDict(frozen=False)

    job_type: JobType = JobType.COMPILE
    type: Literal["CompileJobRef"] = "CompileJobRef"


class ExecuteJobRef(JobRef, BaseRef):
    """Proxy object to an ExecuteJob in Nexus."""

    model_config = ConfigDict(frozen=False)

    job_type: JobType = JobType.EXECUTE
    type: Literal["ExecuteJobRef"] = "ExecuteJobRef"


class CompilationResultRef(BaseRef):
    """Proxy object to the results of a circuit compilation in Nexus."""

    annotations: Annotations
    project: ProjectRef
    _input_circuit: CircuitRef | None = None
    _output_circuit: CircuitRef | None = None
    _compilation_passes: DataframableList[CompilationPassRef] | None = None
    id: UUID  # compilation id
    type: Literal["CompilationResultRef"] = "CompilationResultRef"

    def get_input(self) -> CircuitRef:
        """Get the CircuitRef of the original circuit."""
        if self._input_circuit:
            return self._input_circuit

        from qnexus.client.jobs._compile import _fetch_compilation_output

        (self._input_circuit, self._output_circuit) = _fetch_compilation_output(self)
        return self._input_circuit

    def get_output(self) -> CircuitRef:
        """Get the CircuitRef of the compiled circuit."""
        if self._output_circuit:
            return self._output_circuit

        from qnexus.client.jobs._compile import _fetch_compilation_output

        (self._input_circuit, self._output_circuit) = _fetch_compilation_output(self)
        return self._output_circuit

    def get_passes(self) -> DataframableList[CompilationPassRef]:
        """Get information on the compilation passes and the output circuits (if available)."""
        if self._compilation_passes:
            return copy(self._compilation_passes)

        self._compilation_passes = self._get_compile_results()
        return copy(self._compilation_passes)

    def _get_compile_results(
        self,
    ) -> DataframableList[CompilationPassRef]:
        """Utility method to retrieve the passes and output circuit."""
        from qnexus.client.jobs._compile import _fetch_compilation_passes

        passes = _fetch_compilation_passes(self)
        return passes

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


class ResultType(str, Enum):
    """Enum for a results's type."""

    PYTKET = "PYTKET"
    QSYS = "QSYS"


ExecutionProgram: TypeAlias = CircuitRef | HUGRRef
ExecutionResult: TypeAlias = QsysResult | BackendResult


class ExecutionResultRef(BaseRef):
    """Proxy object to the results of a circuit execution through Nexus."""

    annotations: Annotations
    project: ProjectRef
    result_type: ResultType = ResultType.PYTKET
    _input_program: ExecutionProgram | None = None
    _result: ExecutionResult | None = None
    _backend_info: BackendInfo | None = None
    id: UUID
    type: Literal["ExecutionResultRef"] = "ExecutionResultRef"

    def get_input(self) -> ExecutionProgram:
        """Get the Program Ref of the input program."""
        if self._input_program:
            return self._input_program

        (
            self._result,
            self._backend_info,
            self._input_program,
        ) = self._get_execute_results()
        return copy(self._input_program)

    def download_result(self) -> ExecutionResult:
        """Get a copy of the result of the program execution."""
        if self._result:
            return copy(self._result)

        (
            self._result,
            self._backend_info,
            self._input_program,
        ) = self._get_execute_results()
        return copy(self._result)

    def download_backend_info(self) -> BackendInfo:
        """Get a copy of the pytket BackendInfo."""
        if self._backend_info:
            return copy(self._backend_info)

        (
            self._result,
            self._backend_info,
            self._input_program,
        ) = self._get_execute_results()
        return copy(self._backend_info)

    def _get_execute_results(
        self,
    ) -> tuple[ExecutionResult, BackendInfo, ExecutionProgram]:
        """Utility method to retrieve the passes and output circuit."""
        from qnexus.client.jobs._execute import (
            _fetch_pytket_execution_result,
            _fetch_qsys_execution_result,
        )

        match self.result_type:
            case ResultType.PYTKET:
                return _fetch_pytket_execution_result(self)
            case ResultType.QSYS:
                return _fetch_qsys_execution_result(self)
            case _:
                assert_never(self.result_type)

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return self.annotations.df().join(
            pd.DataFrame(
                {
                    "project": self.project.annotations.name,
                    "id": self.id,
                    "result_type": self.result_type,
                },
                index=[0],
            )
        )


class CompilationPassRef(BaseRef):
    """Proxy object to a compilation pass that was applied on a circuit in Nexus."""

    pass_name: str
    input_circuit: CircuitRef
    output_circuit: CircuitRef
    id: UUID
    type: Literal["CompilationPassRef"] = "CompilationPassRef"

    def get_input(self) -> CircuitRef:
        """Get the CircuitRef of the original circuit."""
        return self.input_circuit

    def get_output(self) -> CircuitRef:
        """Get the CircuitRef of the compiled circuit."""
        return self.output_circuit

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "pass name": self.pass_name,
                "input": self.input_circuit.annotations.name,
                "output": self.output_circuit.annotations.name,
                "id": self.id,
            },
            index=[0],
        )


Ref = Annotated[
    Union[
        TeamRef,
        UserRef,
        ProjectRef,
        CircuitRef,
        WasmModuleRef,
        HUGRRef,
        JobRef,
        CompileJobRef,
        ExecuteJobRef,
        CompilationResultRef,
        ExecutionResultRef,
        CompilationPassRef,
    ],
    Field(discriminator="type"),
]


ref_name_to_class: dict[str, Ref] = {
    config_type.__name__: config_type  # type: ignore
    for config_type in BaseRef.__subclasses__()
}


def deserialize_nexus_ref(jsonable: dict[str, Any]) -> Ref:
    """Deserialize something that should be a subclass of BaseRef based on
    the value of its 'type' field."""
    ref_type = jsonable["type"]
    if ref_type in ref_name_to_class.keys():
        ref_class = ref_name_to_class[ref_type]
        return ref_class(**jsonable)  # type: ignore
    raise ValueError(
        f"Cannot deserialize as {ref_type}, no known class matches that value."
    )
