"""Client API for execution in Nexus."""

from typing import Union, cast

from hugr.qsystem.result import QsysResult
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum

import qnexus.exceptions as qnx_exc
from qnexus.client import circuits as circuit_api
from qnexus.client import get_nexus_client
from qnexus.client import hugr as hugr_api
from qnexus.client import qir as qir_api
from qnexus.client.utils import accept_circuits_for_programs
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.models import BackendConfig, StoredBackendInfo, to_pytket_backend_info
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
    QIRRef,
    ResultType,
    WasmModuleRef,
)
from qnexus.models.utils import assert_never


@accept_circuits_for_programs
@merge_properties_from_context
def start_execute_job(
    programs: Union[ExecutionProgram, list[ExecutionProgram]],
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
        [str(p.id) for p in programs]
        if isinstance(programs, list)
        else [str(programs.id)]
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
                "backend_config": backend_config.model_dump(exclude_none=True),
                "user_group": user_group,
                "valid_check": valid_check,
                "postprocess": postprocess,
                "noisy_simulator": noisy_simulator,
                "language": (
                    language.value if isinstance(language, Language) else language
                ),
                "seed": seed,
                "wasm_module_id": str(wasm_module.id) if wasm_module else None,
                "credential_name": credential_name,
                "items": [
                    {"program_id": program_id, "n_shots": n_shot}
                    for program_id, n_shot in zip(program_ids, n_shots)
                ],
            },
        }
    )
    relationships = {
        "project": {"data": {"id": str(project.id), "type": "project"}},
    }
    req_dict = {
        "data": {
            "attributes": attributes_dict,
            "relationships": relationships,
            "type": "job",
        }
    }

    resp = get_nexus_client().post(
        "/api/jobs/v1beta3",
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

    resp = get_nexus_client().get(f"/api/jobs/v1beta3/{execute_job.id}")

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
        # Check if item is in a "final" state and append to results
        if item["status"]["status"] in (
            "CANCELLED",
            "ERROR",
            "DEPLETED",
            "TERMINATED",
            "COMPLETED",
        ):
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


def _fetch_pytket_execution_result(
    result_ref: ExecutionResultRef,
) -> tuple[BackendResult, BackendInfo, Union[CircuitRef, QIRRef]]:
    """Get the results for an execute job item."""
    assert result_ref.result_type == ResultType.PYTKET, "Incorrect result type"

    res = get_nexus_client().get(f"/api/results/v1beta3/{result_ref.id}")
    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    res_dict = res.json()

    program_data = res_dict["data"]["relationships"]["program"]["data"]
    program_id = program_data["id"]
    program_type = program_data["type"]

    input_program: Union[CircuitRef | QIRRef]
    match program_type:
        case "circuit":
            input_program = circuit_api._fetch_by_id(program_id, scope=None)
        case "qir":
            input_program = qir_api._fetch_by_id(program_id, scope=None)
        case _:
            raise ValueError(f"Unknown program type {type}")

    results_data = res_dict["data"]["attributes"]

    results_dict = {k: v for k, v in results_data.items() if v != [] and v is not None}

    backend_result = BackendResult.from_dict(results_dict)

    backend_info_data = next(
        data for data in res_dict["included"] if data["type"] == "backend_snapshot"
    )
    backend_info = to_pytket_backend_info(
        StoredBackendInfo(**backend_info_data["attributes"])
    )

    return (backend_result, backend_info, input_program)


def _fetch_qsys_execution_result(
    result_ref: ExecutionResultRef,
) -> tuple[QsysResult, BackendInfo, HUGRRef | QIRRef]:
    """Get the results of a next-gen Qsys execute job."""
    assert result_ref.result_type == ResultType.QSYS, "Incorrect result type"

    res = get_nexus_client().get(f"/api/qsys_results/v1beta/{result_ref.id}")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    res_dict = res.json()

    input_program_id = res_dict["data"]["relationships"]["program"]["data"]["id"]

    input_program: HUGRRef | QIRRef
    match res_dict["data"]["relationships"]["program"]["data"]["type"]:
        case "hugr":
            input_program = hugr_api._fetch_by_id(
                input_program_id,
                scope=None,
            )
        case "qir":
            input_program = qir_api._fetch_by_id(
                input_program_id,
                scope=None,
            )

    qsys_result = QsysResult(res_dict["data"]["attributes"]["results"])

    backend_info_data = next(
        data for data in res_dict["included"] if data["type"] == "backend_snapshot"
    )
    backend_info = to_pytket_backend_info(
        StoredBackendInfo(**backend_info_data["attributes"])
    )

    return (
        qsys_result,
        backend_info,
        input_program,
    )
