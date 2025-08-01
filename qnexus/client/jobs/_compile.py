"""Client API for compilation in Nexus."""

from typing import Union, cast

from quantinuum_schemas.models.hypertket_config import HyperTketConfig

import qnexus.exceptions as qnx_exc
from qnexus.client import circuits as circuit_api
from qnexus.client import get_nexus_client
from qnexus.client.utils import accept_circuits_for_programs
from qnexus.context import get_active_project, merge_properties_from_context
from qnexus.models import BackendConfig, JobStatusEnum
from qnexus.models.annotations import Annotations, CreateAnnotations, PropertiesDict
from qnexus.models.references import (
    CircuitRef,
    CompilationPassRef,
    CompilationResultRef,
    CompileJobRef,
    DataframableList,
    JobType,
    ProjectRef,
)


@accept_circuits_for_programs
@merge_properties_from_context
def start_compile_job(
    programs: Union[CircuitRef, list[CircuitRef]],
    backend_config: BackendConfig,
    name: str,
    description: str = "",
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    optimisation_level: int = 2,
    credential_name: str | None = None,
    user_group: str | None = None,
    hypertket_config: HyperTketConfig | None = None,
    skip_intermediate_circuits: bool = True,
) -> CompileJobRef:
    """Submit a compile job to be run in Nexus."""
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    match programs:
        case CircuitRef():
            program_ids = [str(programs.id)]
        case list():
            if not all(isinstance(p, CircuitRef) for p in programs):
                raise TypeError("Compile jobs only accept circuits")
            program_ids = [str(p.id) for p in programs]
        case _:
            raise TypeError(
                "Expected programs to be either a CircuitRef or a list of CircuitRefs"
            )

    attributes_dict = CreateAnnotations(
        name=name,
        description=description,
        properties=properties,
    ).model_dump(exclude_none=True)
    attributes_dict.update(
        {
            "job_type": "compile",
            "definition": {
                "job_definition_type": "compile_job_definition",
                "backend_config": backend_config.model_dump(),
                "user_group": user_group,
                "hypertket_config": hypertket_config.model_dump()
                if hypertket_config is not None
                else None,
                "optimisation_level": optimisation_level,
                "credential_name": credential_name,
                "items": [
                    {
                        "program_id": program_id,
                    }
                    for program_id in program_ids
                ],
                "skip_store_intermediate_passes": skip_intermediate_circuits,
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
    res_data_dict = resp.json()["data"]
    return CompileJobRef(
        id=res_data_dict["id"],
        annotations=Annotations.from_dict(res_data_dict["attributes"]),
        job_type=JobType.COMPILE,
        last_status=JobStatusEnum.SUBMITTED,
        last_message="",
        project=project,
        backend_config_store=backend_config,
    )


def _results(
    compile_job: CompileJobRef,
    allow_incomplete: bool = False,
) -> DataframableList[CompilationResultRef]:
    """Get the results from a compile job."""

    resp = get_nexus_client().get(f"/api/jobs/v1beta3/{compile_job.id}")

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )
    resp_data = resp.json()["data"]

    job_status = resp_data["attributes"]["status"]["status"]

    if job_status != "COMPLETED" and not allow_incomplete:
        raise qnx_exc.ResourceFetchFailed(message=f"Job status: {job_status}")

    compilation_ids = [
        item["compilation_id"]
        for item in resp_data["attributes"]["definition"]["items"]
        if item["status"]["status"] == "COMPLETED"
    ]

    compilation_refs: DataframableList[CompilationResultRef] = DataframableList([])

    for compilation_id in compilation_ids:
        comp_record_resp = get_nexus_client().get(
            f"/api/compilations/v1beta2/{compilation_id}",
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
        project = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
            archived=project_details["attributes"]["archived"],
        )

        compilation_refs.append(
            CompilationResultRef(
                id=comp_json["data"]["id"],
                annotations=Annotations.from_dict(comp_json["data"]["attributes"]),
                project=project,
            )
        )

    return compilation_refs


def _fetch_compilation_output(
    compilation_result_ref: CompilationResultRef,
) -> tuple[CircuitRef, CircuitRef]:
    """Get the input/output compiled circuit from a compilation job."""

    resp = get_nexus_client().get(
        f"/api/compilations/v1beta2/{compilation_result_ref.id}"
    )

    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )

    res_dict = resp.json()

    project_id = res_dict["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(
        proj for proj in res_dict["included"] if proj["id"] == project_id
    )
    project = ProjectRef(
        id=project_id,
        annotations=Annotations.from_dict(project_details["attributes"]),
        contents_modified=project_details["attributes"]["contents_modified"],
        archived=project_details["attributes"]["archived"],
    )

    compiled_circuit_id = res_dict["data"]["relationships"]["compiled_circuit"]["data"][
        "id"
    ]
    compiled_circuit_details = next(
        item for item in res_dict["included"] if item["id"] == compiled_circuit_id
    )

    compiled_circuit_ref = CircuitRef(
        id=compiled_circuit_id,
        annotations=Annotations.from_dict(compiled_circuit_details["attributes"]),
        project=project,
    )

    input_circuit_id = res_dict["data"]["relationships"]["original_circuit"]["data"][
        "id"
    ]
    input_circuit_details = next(
        item for item in res_dict["included"] if item["id"] == input_circuit_id
    )

    input_circuit_ref = CircuitRef(
        id=input_circuit_id,
        annotations=Annotations.from_dict(input_circuit_details["attributes"]),
        project=project,
    )

    return input_circuit_ref, compiled_circuit_ref


def _fetch_compilation_passes(
    compilation_result_ref: CompilationResultRef,
) -> DataframableList[CompilationPassRef]:
    """Get summary information on the passes from a compile job."""

    params = {"filter[compilation][id]": str(compilation_result_ref.id)}

    resp = get_nexus_client().get("/api/compilation_passes/v1beta2", params=params)

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
        pass_input_circuit = circuit_api._fetch_by_id(
            pass_input_circuit_id,
            scope=None,
        )
        pass_output_circuit_id = pass_info["relationships"]["compiled_circuit"]["data"][
            "id"
        ]
        pass_output_circuit = circuit_api._fetch_by_id(
            pass_output_circuit_id,
            scope=None,
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
