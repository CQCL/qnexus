from enum import Enum
from typing import Annotated, Literal, TypedDict, Union
from uuid import UUID

import pandas as pd
import rich
from colorama import Fore
from halo import Halo
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)
from pytket import Circuit
from typing_extensions import NotRequired, Unpack

from qnexus.annotations import Annotations
from qnexus.references import ProjectRef, CircuitRef
from pytket.backends.status import StatusEnum, CircuitStatus

from ..exceptions import ResourceCreateFailed, ResourceFetchFailed
from .client import nexus_client
from .circuits import circuit_get
from .models.filters import (
    ExperimentIDFilter,
    ExperimentIDFilterDict,
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


class JobType(str, Enum):
    Execute = "PROCESS"
    Compile = "COMPILE"


class JobTypeFilter(BaseModel):
    """Filter by job type."""

    type: JobType = Field(
        default=[JobType.Execute, JobType.Compile],
        serialization_alias="filter[job_type]",
        description="Filter by project_id",
    )

    model_config = ConfigDict(use_enum_values=True)


class JobTypeFilterDict(TypedDict):
    """Filter by job type (TypedDict)"""

    type: NotRequired[JobType]


class Params(
    PaginationFilter, NameFilter, JobStatusFilter, ExperimentIDFilter, JobTypeFilter
):
    """Params for fetching jobs"""

    pass


class ParamsDict(
    PaginationFilterDict,
    NameFilterDict,
    ExperimentIDFilterDict,
    JobStatusFilterDict,
    JobTypeFilterDict,
):
    """TypedDict form of jobs list params"""


class JobHandle(BaseModel):
    id: UUID
    item_ids: list[int]
    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef


class JobPage(BaseModel):
    handles: list[JobHandle]
    page_number: int
    page_size: int


def submit(
    name: str,
    circuits: Union[CircuitRef, list[CircuitRef]],
    optimisation_level: int,
    project: ProjectRef,
) -> JobHandle:
    """ """

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
        "description": "",
        "circuit_ids": circuit_ids,
        "optimisation_level": optimisation_level,
        "notes": {},
    }

    resp = nexus_client.post(
        "api/v6/jobs/compile/submit",
        json=compile_job_request,
    )
    if resp.status_code != 202:
        raise ResourceCreateFailed(message=resp.text, status_code=resp.status_code)
    return JobHandle(
        id=resp.json()["job_id"],
        item_ids=resp.json()["item_ids"],
        annotations=Annotations(name=name, description=None, properties={}),
        job_type=JobType.Compile,
        last_status=StatusEnum.SUBMITTED,
        last_message="",
        project=project,
    )


def compilation_results(
    compile_job: JobHandle,
) -> list[Circuit]:
    resp = nexus_client.get(
        f"api/v6/jobs/compile/{compile_job.id}",
    )

    if resp.status_code != 200:
        raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

    compilation_ids = [item["compilation_id"] for item in resp.json()["items"]]

    compiled_circuits = []

    for compilation_id in compilation_ids:
        compilation_record_resp = nexus_client.get(
            f"api/v5/experiments/{compile_job.project.id}/compilations/{compilation_id}",
        )

        if compilation_record_resp.status_code != 200:
            raise ResourceFetchFailed(message=resp.text, status_code=resp.status_code)

        compiled_circuit_id = compilation_record_resp.json()[
            "compiled_circuit_submission_id"
        ]

        compiled_circuit = circuit_get(
            CircuitRef(
                id=compiled_circuit_id,
                annotations=Annotations(name="", description="", properties={}),
                project=compile_job.project,
            )
        )

        compiled_circuits.append(compiled_circuit)

    return compiled_circuits
