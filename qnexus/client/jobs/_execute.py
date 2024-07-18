"""Client API for execution in Nexus."""
from typing import Union, cast

from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import StatusEnum

import qnexus.exceptions as qnx_exc
from qnexus.client import circuits as circuit_api
from qnexus.client import nexus_client
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.models import BackendConfig, StoredBackendInfo
from qnexus.models.annotations import Annotations, CreateAnnotations, PropertiesDict
from qnexus.models.references import (
    CircuitRef,
    DataframableList,
    ExecuteJobRef,
    ExecutionResultRef,
    JobType,
    ProjectRef,
)


@merge_properties_from_context
def start_execute_job(  # pylint: disable=too-many-arguments, too-many-locals
    circuits: Union[CircuitRef, list[CircuitRef]],
    n_shots: list[int] | list[None],
    backend_config: BackendConfig,
    name: str,
    description: str = "",
    properties: PropertiesDict | None = None,
    project: ProjectRef | None = None,
    valid_check: bool = True,
    postprocess: bool = True,
    noisy_simulator: bool = True,
    seed: int | None = None,
    credential_name: str | None = None,
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
                "valid_check": valid_check,
                "postprocess": postprocess,
                "noisy_simulator": noisy_simulator,
                "seed": seed,
                "credential_name": credential_name,
                "items": [
                    {"circuit_id": circuit_id, "n_shots": n_shot}
                    for circuit_id, n_shot in zip(circuit_ids, n_shots)
                ],
            },
        }
    )
    relationships = {
        "project": {"data": {"id": str(project.id), "type": "project"}},
        "circuits": {
            "data": [
                {"id": str(circuit_id), "type": "circuit"} for circuit_id in circuit_ids
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

    resp = nexus_client.post(
        "/api/jobs/v1beta",
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
    )


def _results(
    execute_job: ExecuteJobRef,
) -> DataframableList[ExecutionResultRef]:
    """Get the results from an execute job."""

    resp = nexus_client.get(f"/api/jobs/v1beta/{execute_job.id}")

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )
    resp_data = resp.json()["data"]
    job_status = resp_data["attributes"]["status"]["status"]

    if job_status != "COMPLETED":
        # TODO maybe we want to return a partial list of results?
        raise qnx_exc.ResourceFetchFailed(message=f"Job status: {job_status}")

    execute_results: DataframableList[ExecutionResultRef] = DataframableList([])

    for item in resp_data["attributes"]["definition"]["items"]:
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
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

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
