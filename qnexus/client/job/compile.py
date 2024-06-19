"""Module for compilation in Nexus."""
from typing import Union, cast

from pytket.backends.status import StatusEnum
from typing_extensions import Unpack

import qnexus.exceptions as qnx_exc
from qnexus.client import circuit as circuit_api
from qnexus.client import nexus_client
from qnexus.client.models.annotations import (
    Annotations,
    CreateAnnotations,
    CreateAnnotationsDict,
)
from qnexus.client.models.nexus_dataclasses import BackendConfig
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.references import (
    CircuitRef,
    CompilationPassRef,
    CompilationResultRef,
    CompileJobRef,
    DataframableList,
    JobType,
    ProjectRef,
)


@merge_properties_from_context
def compile(  # pylint: disable=too-many-arguments
    circuits: Union[CircuitRef, list[CircuitRef]],
    backend_config: BackendConfig,
    optimisation_level: int = 2,
    project: ProjectRef | None = None,
    **kwargs: Unpack[CreateAnnotationsDict],
) -> CompileJobRef:
    """Submit a compile job to be run in Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    circuit_ids = (
        [str(circuits.id)]
        if isinstance(circuits, CircuitRef)
        else [str(c.id) for c in circuits]
    )

    annotations = CreateAnnotations(**kwargs)

    compile_job_request = {
        "backend": backend_config.model_dump(),
        "experiment_id": str(project.id),
        "name": annotations.name,
        "description": annotations.description,
        "properties": annotations.properties,
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
    return CompileJobRef(
        id=resp.json()["job_id"],
        annotations=Annotations(
            # TODO add once v1beta jobs api is ready
            name=annotations.name,
            description=annotations.description,
        ),
        job_type=JobType.COMPILE,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )


def _results(
    compile_job: CompileJobRef,
) -> DataframableList[CompilationResultRef]:
    """Get the results from a compile job."""

    resp = nexus_client.get(
        f"api/v6/jobs/compile/{compile_job.id}",
    )

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )

    job_status = resp.json()["job"]["job_status"]["status"]

    if job_status != "COMPLETED":
        raise qnx_exc.ResourceFetchFailed(message=f"Job status: {job_status}")

    compilation_ids = [item["compilation_id"] for item in resp.json()["items"]]

    compilation_refs: DataframableList[CompilationResultRef] = DataframableList([])

    for compilation_id in compilation_ids:
        comp_record_resp = nexus_client.get(
            f"/api/compilations/v1beta/{compilation_id}",
        )

        if comp_record_resp.status_code != 200:
            raise qnx_exc.ResourceFetchFailed(
                message=comp_record_resp.text, status_code=comp_record_resp.status_code
            )

        comp_json = comp_record_resp.json()

        project_id = comp_json["data"]["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in comp_json["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
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

        pass_input_circuit_id = pass_info["relationships"]["original_circuit"]["data"][
            "id"
        ]
        pass_input_circuit = circuit_api._fetch(  # pylint: disable=protected-access
            pass_input_circuit_id
        )
        pass_output_circuit_id = pass_info["relationships"]["compiled_circuit"]["data"][
            "id"
        ]
        pass_output_circuit = circuit_api._fetch(  # pylint: disable=protected-access
            pass_output_circuit_id
        )

        pass_list.append(
            CompilationPassRef(
                pass_name=pass_name,
                input_circuit=pass_input_circuit,
                output_circuit=pass_output_circuit,
                id=pass_info["id"],
            )
        )

    return pass_list
