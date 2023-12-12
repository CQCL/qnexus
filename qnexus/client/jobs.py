from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, TypedDict, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from pytket import Circuit
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.backendresult import BackendResult
from pytket.backends.status import CircuitStatus, StatusEnum
from typing_extensions import NotRequired, Unpack
from qnexus.annotations import Annotations

from qnexus.client.models.utils import AllowNone
from qnexus.references import (
    CircuitRef, 
    JobRef, 
    ProjectRef, 
    JobType, 
    CompilationResultRef, 
    ExecutionResultRef
)

from ..exceptions import ResourceCreateFailed, ResourceFetchFailed
from .client import nexus_client
from .models.filters import (
    ProjectIDFilter,
    ProjectIDFilterDict,
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
)


class JobStatusFilter(BaseModel):
    """Job status filter"""

    status: list[
        Union[
            Literal["COMPLETED"],
            Literal["QUEUED"],
            Literal["SUBMITTED"],
            Literal["RUNNING"],
            Literal["CANCELLED"],
            Literal["ERROR"],
        ]
    ] = Field(
        default=["COMPLETED", "QUEUED", "SUBMITTED", "RUNNING", "CANCELLED", "ERROR"],
        serialization_alias="filter[job_status.status]",
        description="Filter by job status",
    )


class JobStatusFilterDict(TypedDict):
    """Job status filter (TypedDict)"""

    status: NotRequired[
        list[
            Union[
                Literal["COMPLETED"],
                Literal["QUEUED"],
                Literal["SUBMITTED"],
                Literal["RUNNING"],
                Literal["CANCELLED"],
                Literal["ERROR"],
            ]
        ]
    ]


class JobTypeFilter(BaseModel):
    """Filter by job type."""

    type: JobType = Field(
        default=[JobType.Execute, JobType.Compile],
        serialization_alias="filter[job_type]",
        description="Filter by project_id",
    )
    submitted_after: Annotated[datetime, AllowNone] = Field(
        default=None,
        serialization_alias="filter[submitted_after]",
        description="Show jobs submitted after this date.",
    )

    model_config = ConfigDict(use_enum_values=True)


class JobTypeFilterDict(TypedDict):
    """Filter by job type (TypedDict)"""

    type: NotRequired[JobType]
    submitted_after: NotRequired[datetime]


class Params(
    PaginationFilter, NameFilter, JobStatusFilter, ProjectIDFilter, JobTypeFilter
):
    """Params for fetching jobs"""

    pass


class ParamsDict(
    PaginationFilterDict,
    NameFilterDict,
    ProjectIDFilterDict,
    JobStatusFilterDict,
    JobTypeFilterDict,
):
    """TypedDict form of jobs list params"""


# TODO: How should we do lazy loading and pages.
class JobPage(BaseModel):
    jobs: list[JobRef]
    page_number: int
    page_size: int
    total_pages: int
    total_count: int


# @Halo(text="Listing jobs...", spinner="simpleDotsScrolling")
def jobs(**kwargs: Unpack[ParamsDict]) -> JobPage:
    """
    List jobs.
    """
    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True, mode=""
    )

    res = nexus_client.get(
        "/api/v6/jobs",
        params=params,
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()
    data = res_dict["data"]
    meta = res_dict["meta"]

    return JobPage(
        jobs=[
            JobRef(
                id=entry["job_id"],
                annotations=Annotations(name=entry["name"]),
                job_type=entry["job_type"],
                last_status=CircuitStatus.from_dict(entry["job_status"]).status,
                last_message=CircuitStatus.from_dict(entry["job_status"]).message,
                project=ProjectRef(
                    id=entry["experiment_id"],
                    annotations=Annotations(name="placeholder"),
                ),
            )
            for entry in data
        ],
        page_number=meta["page_number"],
        page_size=meta["page_size"],
        total_count=meta["total_count"],
        total_pages=meta["total_pages"],
    )


def retry_error(job: JobRef):
    if job.job_type != JobType.Execute:
        raise Exception("Invalid job type")

    res = nexus_client.post(
        "/api/v6/jobs/process/retry_check", json={"job_id": str(job.id)}
    )

    if res.status_code != 202:
        res.raise_for_status()


def retry_submission(job: JobRef):
    if job.job_type != JobType.Execute:
        raise Exception("Invalid job type")

    res = nexus_client.post(
        "/api/v6/jobs/process/retry_submit",
        json={"job_id": str(job.id), "resubmit_to_backend": True},
    )

    if res.status_code != 202:
        res.raise_for_status()


def submit_compile_job(
    name: str,
    circuits: Union[CircuitRef, list[CircuitRef]],
    optimisation_level: int,
    project: ProjectRef,
    description: str | None = None
) -> JobRef:
    """ """

    # TODO what happens if they submit a circuit that belongs to another project?

    circuit_ids = (
        [str(circuits.id)]
        if isinstance(circuits, CircuitRef)
        else [str(c.id) for c in circuits]
    )

    compile_job_request = {
        "backend": {
            "type": "AerConfig",
            "noise_model": None,
            "simulation_method": "automatic",
            "n_qubits": 40,
            "seed": None,
        },
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


def submit_execute_job(
    name: str,
    circuits: Union[CircuitRef, list[CircuitRef]],
    project: ProjectRef,
    n_shots: list[int] | list[None],
    batch_id: str | None = None,
    valid_check: bool = True,
    postprocess: bool | None = None,
    noisy_simulator: bool | None = None,
    seed: int | None = None,
    description: str | None = None
) -> JobRef:
    """ """

    circuit_ids = (
        [str(circuits.id)]
        if isinstance(circuits, CircuitRef)
        else [str(c.id) for c in circuits]
    )

    if any(n_shots) and len(n_shots) != len(circuit_ids):
        raise ValueError("Number of circuits must equal number of n_shots.")
    else:
        n_shots = [None] * len(circuit_ids)

    execute_job_request = {
        "backend": {
            "type": "AerConfig",
            "noise_model": None,
            "simulation_method": "automatic",
            "n_qubits": 40,
            "seed": None,
        },
        "experiment_id": str(project.id),
        "name": name,
        "items": [
            {"circuit_id": circuit_id, "n_shots" : n_shot}
            for circuit_id, n_shot in zip(circuit_ids, n_shots)
        ],
        "batch_id": batch_id,
        "valid_check": valid_check,
        "postprocess": postprocess,
        "noisy_simulator": noisy_simulator,
        "seed": seed,
        "description": description,
    }

    resp = nexus_client.post(
        "api/v6/jobs/process/submit",
        json=execute_job_request,
    )
    if resp.status_code != 202:
        raise ResourceCreateFailed(message=resp.text, status_code=resp.status_code)
    return JobRef(
        id=resp.json()["job_id"],
        annotations=Annotations(name=name, description=description, properties={}),
        job_type=JobType.Execute,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )    


def compilation_results(
    compile_job: JobRef,
) -> list[CircuitRef]: # TODO replace with CompilationResultRef
    """ """

    resp = nexus_client.get(
        f"api/v6/jobs/compile/{compile_job.id}",
    )

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    compilation_ids = [item["compilation_id"] for item in resp.json()["items"]]

    compiled_circuits: list[CircuitRef] = []

    for compilation_id in compilation_ids:
        compilation_record_resp = nexus_client.get(
            f"api/v5/experiments/{compile_job.project.id}/compilations/{compilation_id}",
        )

        if compilation_record_resp.status_code != 200:
            raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

        compiled_circuit_id = compilation_record_resp.json()[
            "compiled_circuit_submission_id"
        ]

        circuit = CircuitRef(
            id=compiled_circuit_id,
            annotations=Annotations(name="", description="", properties={}),
            project=compile_job.project,
        )
        circuit.get_circuit()
        

        compiled_circuits.append(circuit)

    return compiled_circuits


def execution_results(
    execute_job: JobRef,
) -> list[ExecutionResultRef]:
    """ """

    resp = nexus_client.get(
        f"api/v6/jobs/process/{execute_job.id}",
    )

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    results:list[ExecutionResultRef]  = []

    for item in resp.json()["items"]:

        result_ref = ExecutionResultRef(id=item["result_id"], annotations=execute_job.annotations, project=execute_job.project)

        result_ref.get_result()

        results.append(result_ref)

    return results
