"""Client API for execution in Nexus."""

from logging import getLogger
from typing import NewType, Tuple, Union, cast

from guppylang.qsys_result import QsysResult
from pytket.architecture import Architecture, FullyConnected
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum
from pytket.circuit import Node, OpType
from quantinuum_schemas.models.backend_info import Register

import qnexus.exceptions as qnx_exc
from qnexus.client import circuits as circuit_api
from qnexus.client import get_nexus_client
from qnexus.client import hugr as hugr_api
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.models import BackendConfig, StoredBackendInfo
from qnexus.models.annotations import Annotations, CreateAnnotations, PropertiesDict
from qnexus.models.language import Language
from qnexus.models.references import (
    CircuitRef,
    DataframableList,
    ExecuteJobRef,
    ExecutionProgram,
    ExecutionResultRef,
    HUGRRef,
    JobType,
    ProjectRef,
    ResultType,
    WasmModuleRef,
)
from qnexus.models.utils import assert_never

logger = getLogger(__name__)


@merge_properties_from_context
def start_execute_job(
    circuits: Union[ExecutionProgram, list[ExecutionProgram]],
    n_shots: list[int] | list[None],
    backend_config: BackendConfig,
    name: str,
    description: str = "",
    properties: PropertiesDict | None = None,
    project: ProjectRef | None = None,
    valid_check: bool = True,
    postprocess: bool = False,
    noisy_simulator: bool = True,
    language: Language = Language.AUTO,
    seed: int | None = None,
    credential_name: str | None = None,
    wasm_module: WasmModuleRef | None = None,
    user_group: str | None = None,
) -> ExecuteJobRef:
    """
    Submit an execute job to be run in Nexus. Returns an ``ExecuteJobRef``
    object which can be used to check the job's status.  See ``qnexus.execute``
    for a utility method that waits for the results and returns them.
    """
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    program_ids = (
        [str(p.id) for p in circuits]
        if isinstance(circuits, list)
        else [str(circuits.id)]
    )

    if len(n_shots) != len(program_ids):
        raise ValueError("Number of programs must equal number of n_shots.")

    attributes_dict = CreateAnnotations(
        name=name,
        description=description,
        properties=properties,
    ).model_dump(exclude_none=True)
    attributes_dict.update(
        {
            "job_type": "execute",
            "definition": {
                "job_definition_type": "execute_job_definition",
                "backend_config": backend_config.model_dump(),
                "user_group": user_group,
                "valid_check": valid_check,
                "postprocess": postprocess,
                "noisy_simulator": noisy_simulator,
                "language": language.value
                if isinstance(language, Language)
                else language,
                "seed": seed,
                "wasm_module_id": str(wasm_module.id) if wasm_module else None,
                "credential_name": credential_name,
                "items": [
                    {"circuit_id": program_id, "n_shots": n_shot}
                    for program_id, n_shot in zip(program_ids, n_shots)
                ],
            },
        }
    )
    relationships = {
        "project": {"data": {"id": str(project.id), "type": "project"}},
        "circuits": {
            "data": [
                {"id": str(program_id), "type": "circuit"} for program_id in program_ids
            ]
        },
    }
    req_dict = {
        "data": {
            "attributes": attributes_dict,
            "relationships": relationships,
            "type": "job",
        }
    }

    resp = get_nexus_client().post(
        "/api/jobs/v1beta2",
        json=req_dict,
    )
    if resp.status_code != 202:
        raise qnx_exc.ResourceCreateFailed(
            message=resp.text, status_code=resp.status_code
        )

    return ExecuteJobRef(
        id=resp.json()["data"]["id"],
        annotations=Annotations.from_dict(resp.json()["data"]["attributes"]),
        job_type=JobType.EXECUTE,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
        backend_config_store=backend_config,
    )


def _results(
    execute_job: ExecuteJobRef,
    allow_incomplete: bool = False,
) -> DataframableList[ExecutionResultRef]:
    """Get the results from an execute job."""

    resp = get_nexus_client().get(f"/api/jobs/v1beta2/{execute_job.id}")

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )
    resp_data = resp.json()["data"]
    job_status = resp_data["attributes"]["status"]["status"]

    if job_status != "COMPLETED" and not allow_incomplete:
        raise qnx_exc.ResourceFetchFailed(message=f"Job status: {job_status}")

    execute_results: DataframableList[ExecutionResultRef] = DataframableList([])

    for item in resp_data["attributes"]["definition"]["items"]:
        if item["status"]["status"] == "COMPLETED":
            result_type: ResultType

            match item["result_type"]:
                case ResultType.QSYS:
                    result_type = ResultType.QSYS
                case ResultType.PYTKET:
                    result_type = ResultType.PYTKET
                case _:
                    assert_never(item["result_type"])

            result_ref = ExecutionResultRef(
                id=item["result_id"],
                annotations=execute_job.annotations,
                project=execute_job.project,
                result_type=result_type,
            )

            execute_results.append(result_ref)

    return execute_results


def _register_to_pytket_node(register: Register) -> Node:
    """Convert a pytket Node object from a nexus-dataclasses Register object."""

    return Node.from_list(list(register))


def _to_pytket_backend_info(backend: StoredBackendInfo) -> BackendInfo:
    """Reconstruct a pytket BackendInfo from the StoredBackendInfo instance."""

    stored_nodes = backend.device.nodes
    stored_edges = backend.device.edges
    architecture_edge_list = []

    # BackendInfo dictionary attributes are initialised as None,
    # Then dictionaries are built when they are to be populated.
    # This is to satisfy type-checking as well as BackendInfo expectations/tests.

    averaged_node_gate_errors = None
    averaged_readout_errors = None
    all_node_gate_errors = None
    all_readout_errors = None

    for stored_node in stored_nodes:
        # Create node from register
        new_pytket_node = _register_to_pytket_node(stored_node.unitid)

        # Build average node gate errors
        if stored_node.average_error is not None:
            if averaged_node_gate_errors is None:
                averaged_node_gate_errors = {}
            averaged_node_gate_errors[new_pytket_node] = stored_node.average_error
        # Build average readout errors
        if stored_node.readout_error is not None:
            if averaged_readout_errors is None:
                averaged_readout_errors = {}
            averaged_readout_errors[new_pytket_node] = stored_node.readout_error

        if stored_node.gate_errors:
            node_gate_errors = {
                getattr(OpType, optype_name): error
                for optype_name, error in stored_node.gate_errors.items()
            }
            if all_node_gate_errors is None:
                all_node_gate_errors = {}
            all_node_gate_errors[new_pytket_node] = node_gate_errors

        # Add stored_node readout errors to all_readout_errors
        stored_zero_state_readout_error = stored_node.zero_state_readout_error
        stored_one_state_readout_error = stored_node.one_state_readout_error
        if (
            stored_zero_state_readout_error is not None
            and stored_one_state_readout_error is not None
        ):
            if all_readout_errors is None:
                all_readout_errors = {}
            readout_errors = [
                [
                    1.0 - stored_zero_state_readout_error,
                    stored_zero_state_readout_error,
                ],
                [
                    stored_one_state_readout_error,
                    1.0 - stored_one_state_readout_error,
                ],
            ]
            all_readout_errors[new_pytket_node] = readout_errors

    # Build all_edge_gate_errors and averaged_edge_gate_errors from stored_edges
    all_edge_gate_errors = None
    averaged_edge_gate_errors = None

    for stored_edge in stored_edges:
        node_from = _register_to_pytket_node(stored_edge.unitid_from)
        node_to = _register_to_pytket_node(stored_edge.unitid_to)

        new_edge_tuple = (node_from, node_to)
        architecture_edge_list.append(new_edge_tuple)

        if stored_edge.average_error is not None:
            if averaged_edge_gate_errors is None:
                averaged_edge_gate_errors = {}
            averaged_edge_gate_errors[(node_from, node_to)] = stored_edge.average_error
        if stored_edge.gate_errors:
            edge_gate_errors = {
                getattr(OpType, optype_name): error
                for optype_name, error in stored_edge.gate_errors.items()
            }
            if all_edge_gate_errors is None:
                all_edge_gate_errors = {}
            all_edge_gate_errors[(node_from, node_to)] = edge_gate_errors

    architecture: Union[Architecture, FullyConnected] = (
        FullyConnected(
            backend.device.n_nodes
            if backend.device.n_nodes is not None
            else len(backend.device.nodes)
        )
        if backend.device.fully_connected
        else Architecture(architecture_edge_list)
    )

    gate_set = set()

    for gate in backend.gate_set:
        try:
            gate_set.add(getattr(OpType, gate))
        except AttributeError:
            logger.warning(
                "Unknown OpType in BackendInfo: `%`, will omit from BackendInfo."
                " Consider updating your pytket version."
            )

    return BackendInfo(
        name=backend.name,
        device_name=backend.device_name,
        version=backend.version,
        architecture=architecture,
        gate_set=gate_set,
        n_cl_reg=backend.n_cl_reg,
        supports_fast_feedforward=backend.supports_fast_feedforward,
        supports_reset=backend.supports_reset,
        supports_midcircuit_measurement=backend.supports_midcircuit_measurement,
        all_node_gate_errors=all_node_gate_errors,
        all_edge_gate_errors=all_edge_gate_errors,
        all_readout_errors=all_readout_errors,
        averaged_node_gate_errors=averaged_node_gate_errors,
        averaged_edge_gate_errors=averaged_edge_gate_errors,
        averaged_readout_errors=averaged_readout_errors,
        misc=backend.misc,
    )


def _fetch_pytket_execution_result(
    result_ref: ExecutionResultRef,
) -> tuple[BackendResult, BackendInfo, CircuitRef]:
    """Get the results for an execute job item."""
    assert result_ref.result_type == ResultType.PYTKET, "Incorrect result type"

    res = get_nexus_client().get(f"/api/results/v1beta3/{result_ref.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    res_dict = res.json()

    input_circuit_id = res_dict["data"]["relationships"]["circuit"]["data"]["id"]

    input_circuit = circuit_api._fetch_by_id(
        input_circuit_id,
        scope=None,
    )

    results_data = res_dict["data"]["attributes"]

    results_dict = {k: v for k, v in results_data.items() if v != [] and v is not None}

    backend_result = BackendResult.from_dict(results_dict)

    backend_info_data = next(
        data for data in res_dict["included"] if data["type"] == "backend_snapshot"
    )
    backend_info = _to_pytket_backend_info(
        StoredBackendInfo(**backend_info_data["attributes"])
    )

    return (backend_result, backend_info, input_circuit)


def _fetch_qsys_execution_result(
    result_ref: ExecutionResultRef,
) -> tuple[QsysResult, BackendInfo, HUGRRef]:
    """Get the results of a next-gen Qsys execute job."""
    assert result_ref.result_type == ResultType.QSYS, "Incorrect result type"

    res = get_nexus_client().get(f"/api/qsys_results/v1beta/{result_ref.id}")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    res_dict = res.json()

    input_hugr_id = res_dict["data"]["relationships"]["hugr_module"]["data"]["id"]

    input_hugr = hugr_api._fetch_by_id(
        input_hugr_id,
        scope=None,
    )

    qsys_result = QsysResult(res_dict["data"]["attributes"]["results"])

    backend_info_data = next(
        data for data in res_dict["included"] if data["type"] == "backend_snapshot"
    )
    backend_info = _to_pytket_backend_info(
        StoredBackendInfo(**backend_info_data["attributes"])
    )

    return (
        qsys_result,
        backend_info,
        input_hugr,
    )
