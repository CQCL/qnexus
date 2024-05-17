"""Client API for execution in Nexus."""
from typing import Union, Unpack, cast

from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum

from qnexus.client import nexus_client
from qnexus.client import circuit as circuit_api
from qnexus.client.models.annotations import (
    Annotations,
    CreateAnnotations,
    CreateAnnotationsDict,
    PropertiesDict,
)
from qnexus.client.models.nexus_dataclasses import BackendConfig, StoredBackendInfo
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.exceptions import ResourceCreateFailed, ResourceFetchFailed
from qnexus.references import (
    CircuitRef,
    DataframableList,
    ExecutionResultRef,
    ExecuteJobRef,
    JobType,
    ProjectRef,
)


@merge_properties_from_context
def _execute(  # pylint: disable=too-many-arguments
    circuits: Union[CircuitRef, list[CircuitRef]],
    n_shots: list[int] | list[None],
    target: BackendConfig,
    project: ProjectRef | None = None,
    batch_id: str | None = None,
    valid_check: bool = True,
    postprocess: bool | None = None,
    noisy_simulator: bool | None = None,
    seed: int | None = None,
    **kwargs: Unpack[CreateAnnotationsDict],
) -> ExecuteJobRef:
    """Submit a execute job to be run in Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    circuit_ids = (
        [str(circuits.id)]
        if isinstance(circuits, CircuitRef)
        else [str(c.id) for c in circuits]
    )

    if len(n_shots) != len(circuit_ids):
        raise ValueError("Number of circuits must equal number of n_shots.")

    annotations = CreateAnnotations(**kwargs)

    execute_job_request = {
        "backend": target.model_dump(),
        "experiment_id": str(project.id),
        "name": annotations.name,
        "items": [
            {"circuit_id": circuit_id, "n_shots": n_shot}
            for circuit_id, n_shot in zip(circuit_ids, n_shots)
        ],
        "batch_id": batch_id,
        "valid_check": valid_check,
        "postprocess": postprocess,
        "noisy_simulator": noisy_simulator,
        "seed": seed,
        "description": annotations.description,
        "properties": annotations.properties,
    }

    resp = nexus_client.post(
        "api/v6/jobs/process/submit",
        json=execute_job_request,
    )
    if resp.status_code != 202:
        raise ResourceCreateFailed(message=resp.text, status_code=resp.status_code)
    return ExecuteJobRef(
        id=resp.json()["job_id"],
        annotations=annotations,
        job_type=JobType.EXECUTE,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )


def _results(
    execute_job: ExecuteJobRef,
) -> DataframableList[ExecutionResultRef]:
    """Get the results from an execute job."""

    resp = nexus_client.get(
        f"api/v6/jobs/process/{execute_job.id}",
    )

    # TODO make sure job is complete

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    execute_results: DataframableList[ExecutionResultRef] = DataframableList([])

    for item in resp.json()["items"]:
        result_ref = ExecutionResultRef(
            id=item["result_id"],
            annotations=execute_job.annotations,
            project=execute_job.project,
        )

        execute_results.append(result_ref)

    return execute_results


def _fetch_execution_result(
    handle: ExecutionResultRef,
) -> tuple[BackendResult, BackendInfo, CircuitRef]:
    """Get the results for an execute job item."""
    res = nexus_client.get(f"/api/results/v1beta/{handle.id}")
    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    input_circuit_id = res_dict["data"]["relationships"]["circuit"]["data"]["id"]

    input_circuit = circuit_api._fetch(  # pylint: disable=protected-access
        input_circuit_id
    )

    results_data = res_dict["data"]["attributes"]

    results_dict = {k: v for k, v in results_data.items() if v != [] and v is not None}

    backend_result = BackendResult.from_dict(results_dict)

    backend_info_data = next(
        data for data in res_dict["included"] if data["type"] == "backend_snapshot"
    )
    backend_info = StoredBackendInfo(
        **backend_info_data["attributes"]
    ).to_pytket_backend_info()

    return (backend_result, backend_info, input_circuit)
