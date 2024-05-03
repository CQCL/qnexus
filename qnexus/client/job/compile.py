"""Client API for compilation in Nexus."""
from typing import Union, cast

from pytket.backends.status import StatusEnum

import qnexus.exceptions as qnx_exc
from qnexus.client import circuit as circuit_api
from qnexus.client import nexus_client
from qnexus.client.models.annotations import Annotations, PropertiesDict
from qnexus.client.models.nexus_dataclasses import BackendConfig
from qnexus.context import get_active_project
from qnexus.references import (
    CircuitRef,
    CompilationPassRef,
    CompilationResultRef,
    DataframableList,
    JobRef,
    JobType,
    ProjectRef,
)


def _compile(  # pylint: disable=too-many-arguments
    name: str,
    circuits: Union[CircuitRef, list[CircuitRef]],
    optimisation_level: int,
    target: BackendConfig,
    project: ProjectRef | None = None,
    description: str | None = None,
) -> JobRef:
    """Submit a compile job to be run in Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    circuit_ids = (
        [str(circuits.id)]
        if isinstance(circuits, CircuitRef)
        else [str(c.id) for c in circuits]
    )

    compile_job_request = {
        "backend": target.model_dump(),
        "experiment_id": str(project.id),
        "name": name,
        "description": description,
        "circuit_ids": circuit_ids,
        "optimisation_level": optimisation_level,
    }

    resp = nexus_client.post(
        "api/v6/jobs/compile/submit",
        json=compile_job_request,
    )
    if resp.status_code != 202:
        raise qnx_exc.ResourceCreateFailed(
            message=resp.text, status_code=resp.status_code
        )
    return JobRef(
        id=resp.json()["job_id"],
        annotations=Annotations(
            name=name, description=description, properties=PropertiesDict({})
        ),
        job_type=JobType.COMPILE,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )


def results(
    compile_job: JobRef,
) -> DataframableList[CompilationResultRef]:
    """Get the results from a compile job."""

    resp = nexus_client.get(
        f"api/v6/jobs/compile/{compile_job.id}",
    )

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )

    compilation_ids = [item["compilation_id"] for item in resp.json()["items"]]

    compilation_refs: DataframableList[CompilationResultRef] = DataframableList([])

    for compilation_id in compilation_ids:
        compilation_record_resp = nexus_client.get(
            f"/api/compilations/v1beta/{compilation_id}",
        )

        if compilation_record_resp.status_code != 200:
            raise qnx_exc.ResourceFetchFailed(
                message=resp.text, status_code=resp.status_code
            )

        comp_json = compilation_record_resp.json()

        project_id = comp_json["data"]["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in comp_json["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
        )

        compilation_refs.append(
            CompilationResultRef(
                id=comp_json["data"]["id"],
                annotations=Annotations.from_dict(comp_json["data"]["attributes"]),
                project=project_ref,
            )
        )

    return compilation_refs


def _fetch_compilation_passes(
    compilation_result_ref: CompilationResultRef,
) -> DataframableList[CompilationPassRef]:
    """Get summary information on the passes from a compile job."""

    params = {"filter[compilation][id]": str(compilation_result_ref.id)}

    resp = nexus_client.get("/api/compilation_passes/v1beta", params=params)

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )

    pass_json = resp.json()
    pass_list: DataframableList[CompilationPassRef] = DataframableList([])

    for pass_info in pass_json["data"]:
        pass_name = pass_info["attributes"]["pass_name"]

        pass_result_circuit_id = pass_info["relationships"]["compiled_circuit"]["data"][
            "id"
        ]

        pass_result_circuit = circuit_api._fetch(  # pylint: disable=protected-access
            pass_result_circuit_id
        )
        pass_list.append(
            CompilationPassRef(
                pass_name=pass_name, circuit=pass_result_circuit, id=pass_info["id"]
            )
        )

    return pass_list
