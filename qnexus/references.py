from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pytket.circuit import Circuit
from pytket.backends.backendinfo import Architecture, BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum

from qnexus.annotations import Annotations
from qnexus.client.client import nexus_client
from qnexus.exceptions import ResourceFetchFailed

class BaseRef(BaseModel):
    model_config = ConfigDict(frozen=True)


class ProjectRef(BaseRef):
    id: UUID
    annotations: Annotations


class CircuitRef(BaseRef):
    id: UUID
    annotations: Annotations
    project: ProjectRef

    _circuit: Circuit | None = None

    def get_circuit(self):
        if not self._circuit:
            self._circuit = _fetch_circuit(self)
        return self._circuit


class JobType(str, Enum):
    Execute = "PROCESS"
    Compile = "COMPILE"


class JobRef(BaseRef):
    id: UUID
    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef


class CompilationResultRef(BaseRef):
    id: UUID
    annotations: Annotations
    project: ProjectRef

    # compile job results include:
    # - compilation passes (circuits and pass names)
    # - compiled circuits

    _compiled_circuit: Circuit | None = None

    def get_compiled_circuit(self):
        if not self._compiled_circuit:
            pass # TODO
        return self._compiled_circuit



class ExecutionResultRef(BaseRef):
    id: UUID
    annotations: Annotations
    project: ProjectRef

    _result: BackendResult | None = None
    _backend_info: BackendInfo | None = None
    
    def get_result(self):
        if not self._result:
            self._result, self._backend_info = _fetch_execution_result(self)
        return self._result

    def get_backend_info(self):
        if not self._backend_info:
            self._result, self._backend_info = _fetch_execution_result(self)
        return self._backend_info


def _fetch_circuit(handle: CircuitRef) -> Circuit:
    res = nexus_client.get(f"/api/circuits/v1beta/{handle.id}")
    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_data_attributes_dict = res.json()["data"]["attributes"]
    circuit_dict = {k: v for k, v in res_data_attributes_dict.items() if v is not None}

    return Circuit.from_dict(circuit_dict)


def _fetch_execution_result(handle: ExecutionResultRef) -> tuple[BackendResult, BackendInfo]:
    res = nexus_client.get(f"/api/results/v1beta/{handle.id}")
    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    results_data = res.json()["data"]["attributes"]
    results_dict = {k: v for k, v in results_data.items() if v != [] and v is not None}


    backend_result = BackendResult.from_dict(results_dict)

    # TODO
    backend_info = BackendInfo(
        name="", 
        device_name="",
        version="",
        architecture=Architecture(),
        gate_set=set(),
    )
    
    return (backend_result, backend_info)


