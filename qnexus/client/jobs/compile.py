from typing import Union, cast

from nexus_dataclasses.backend_config import BackendConfig
from pytket.backends.status import StatusEnum

from qnexus.annotations import Annotations, PropertiesDict
from qnexus.client import circuits as circuits_api, nexus_client
from qnexus.client.models.filters import (
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    ProjectIDFilter,
    ProjectIDFilterDict,
)
from qnexus.client.models.utils import AllowNone
from qnexus.client.pagination_iterator import RefList
from qnexus.config import get_config
from qnexus.context import get_active_project
from qnexus.exceptions import ResourceCreateFailed, ResourceFetchFailed
from qnexus.references import (
    CircuitRef,
    CompilationResultRef,
    JobRef,
    JobType,
    ProjectRef,
)

config = get_config()


def run(
    name: str,
    circuits: Union[CircuitRef, list[CircuitRef]],
    optimisation_level: int,
    target: BackendConfig,
    project: ProjectRef | None = None,
    description: str | None = None,
) -> JobRef:
    """ """
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    # TODO what happens if they submit a circuit that belongs to another project?

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
        raise ResourceCreateFailed(message=resp.text, status_code=resp.status_code)
    return JobRef(
        id=resp.json()["job_id"],
        annotations=Annotations(name=name, description=description, properties={}),
        job_type=JobType.Compile,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )


def results(
    compile_job: JobRef,
) -> RefList[CompilationResultRef]:
    """ """

    resp = nexus_client.get(
        f"api/v6/jobs/compile/{compile_job.id}",
    )

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    compilation_ids = [item["compilation_id"] for item in resp.json()["items"]]

    compilation_refs = RefList([])

    for compilation_id in compilation_ids:
        compilation_record_resp = nexus_client.get(
            f"/api/compilations/v1beta/{compilation_id}",
        )

        if compilation_record_resp.status_code != 200:
            raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

        comp_json = compilation_record_resp.json()

        project_id = comp_json["data"]["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in comp_json["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations(
                name=project_details["attributes"]["name"],
                description=project_details["attributes"].get("description", None),
                properties=project_details["attributes"]["properties"],
            ),
        )

        compilation_refs.append(
            CompilationResultRef(
                id=comp_json["data"]["id"],
                annotations=Annotations(
                    name=comp_json["data"]["attributes"]["name"],
                    description=comp_json["data"]["attributes"]["description"],
                    properties=PropertiesDict(
                        **comp_json["data"]["attributes"]["properties"]
                    ),
                ),
                project=project_ref,
            )
        )

    return compilation_refs


def _fetch_compilation_passes(
    compilation_result_ref: CompilationResultRef,
) -> list[tuple[str, CircuitRef]]:  # TODO typing
    """ """

    params = {"filter[compilation][id]": str(compilation_result_ref.id)}

    resp = nexus_client.get(f"/api/compilation_passes/v1beta", params=params)

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    pass_json = resp.json()
    pass_list = []

    for pass_info in pass_json["data"]:
        pass_name = pass_info["attributes"]["pass_name"]

        pass_result_circuit_id = pass_info["relationships"]["compiled_circuit"]["data"][
            "id"
        ]

        pass_result_circuit = circuits_api._fetch(pass_result_circuit_id)
        pass_list.append((pass_name, pass_result_circuit))

    return pass_list
