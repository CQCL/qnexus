import asyncio
from datetime import datetime

import json
import ssl
from typing import Annotated, Any, Literal, Optional, TypedDict, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from pytket.backends.status import StatusEnum, WAITING_STATUS
from typing_extensions import NotRequired, Unpack
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

from qnexus.annotations import Annotations
from qnexus.client.models.utils import AllowNone
from qnexus.client.models.job_status import JobStatus
from qnexus.config import Config
from qnexus.references import (
    CircuitRef,
    JobRef,
    ProjectRef,
    JobType,
    RefList,
    ExecutionResultRef,
)

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.models.filters import (
    ProjectIDFilter,
    ProjectIDFilterDict,
    ProjectRefFilter,
    ProjectRefFilterDict,
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
)
from qnexus.client.jobs import execute, compile

from qnexus.client.pagination_iterator import NexusDatabaseIterator
from qnexus.context import merge_project_from_context

config = Config()


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
    # TODO add job id filter
    PaginationFilter, 
    NameFilter, 
    JobStatusFilter, 
    ProjectIDFilter, 
    ProjectRefFilter, 
    JobTypeFilter
):
    """Params for fetching jobs"""

    pass


class ParamsDict(
    PaginationFilterDict,
    NameFilterDict,
    ProjectIDFilterDict,
    ProjectRefFilterDict,
    JobStatusFilterDict,
    JobTypeFilterDict,
):
    """TypedDict form of jobs list params"""



# @Halo(text="Listing jobs...", spinner="simpleDotsScrolling")
@merge_project_from_context
def filter(**kwargs: Unpack[ParamsDict]) -> NexusDatabaseIterator:
    """
    List jobs.
    """

    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True, mode=""
    )
    if project_id_filter := params.pop("filter[project][id]", None):
        # TODO not needed after v1beta jobs api
        params["filter[experiment_id]"] = project_id_filter
    
    return NexusDatabaseIterator(
        resource_type="Job",
        nexus_url="/api/v6/jobs",
        params=params,
        wrapper_method=_to_JobRef
    )


def _to_JobRef(data: dict[str,Any]) -> RefList[JobRef]:
    """ """
    return RefList([
            JobRef(
                id=entry["job_id"],
                annotations=Annotations(name=entry["name"]),
                job_type=entry["job_type"],
                last_status=JobStatus.from_dict(entry["job_status"]).status,
                last_message=JobStatus.from_dict(entry["job_status"]).message,
                project=ProjectRef(
                    id=entry["experiment_id"],
                    annotations=Annotations(name="placeholder"),
                ),
            )
            for entry in data["data"]
        ])

# id: Optional[str] = None,
def get(**kwargs: Unpack[ParamsDict]) -> JobRef:
    """ """
    filter_call = filter(**kwargs)
    if filter_call.count() > 1:
        raise qnx_exc.NoUniqueMatch
    if filter_call.count() == 0:
        raise qnx_exc.ZeroMatches
    return filter_call.all()[0]


<<<<<<< HEAD
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
    description: str | None = None,
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
    description: str | None = None,
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
            {"circuit_id": circuit_id, "n_shots": n_shot}
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
) -> list[CircuitRef]:  # TODO replace with CompilationResultRef
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

        circuit = circuits._fetch(compiled_circuit_id)

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

    results: list[ExecutionResultRef] = []

    for item in resp.json()["items"]:

        result_ref = ExecutionResultRef(
            id=item["result_id"],
            annotations=execute_job.annotations,
            project=execute_job.project,
        )

        result_ref.get_result()

        results.append(result_ref)

    return results


=======
>>>>>>> 948a9e0 (WIP bits)
def wait_for(
    job: JobRef,
    wait_for_status: StatusEnum = StatusEnum.COMPLETED,
    timeout: float | None = 300.0,
) -> JobStatus:
<<<<<<< HEAD
    """Check job status until the job is complete (or a specified status)."""
    return asyncio.run(
=======
    """Check job status until the job is complete (or a specified status).
    """
    job_status = asyncio.run(
>>>>>>> 5858ec5 (Some updated code)
        asyncio.wait_for(
            listen_job_status(job=job, wait_for_status=wait_for_status),
            timeout=timeout,
        )
    )

    if job_status.status == StatusEnum.ERROR:
        raise qnx_exc.JobError(f"Job errored with detail: {job_status.error_detail}")
    return job_status


def status(job: JobRef) -> JobStatus:
    """ """
    resp = nexus_client.get(f"api/v6/jobs/{job.id}/status")
    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=resp.text, status_code=resp.status_code)
    job_status = JobStatus.from_dict(resp.json())
    # job.last_status = job_status.status
    return job_status


async def listen_job_status(
    job: JobRef, wait_for_status: StatusEnum = StatusEnum.COMPLETED
) -> JobStatus:
    """Check the Status of a Job via a websocket connection.
    Will use SSO tokens."""
    job_status = status(job)
    # logger.debug("Current job status: %s", job_status.status)
    if job_status.status not in WAITING_STATUS or job_status.status == wait_for_status:
        return job_status

    # If we pass True into the websocket connection, it sets a default SSLContext.
    # See: https://websockets.readthedocs.io/en/stable/reference/client.html
    ssl_reconfigured: Union[bool, ssl.SSLContext] = True
    # if not nexus_config.verify_session:
    #     ssl_reconfigured = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #     ssl_reconfigured.check_hostname = False
    #     ssl_reconfigured.verify_mode = ssl.CERT_NONE

    extra_headers = {
        # TODO, this cookie will expire frequently
        "Cookie": f"myqos_id={nexus_client.auth.cookies.get('myqos_id')}"  # type: ignore
    }
    async for websocket in connect(
        f"{config.websockets_url}/api/v6/jobs/{job.id}/status/ws",
        ssl=ssl_reconfigured,
        extra_headers=extra_headers,
        # logger=logger,
    ):
        try:
            async for status_json in websocket:
                # logger.debug("New status: %s", status_json)
                job_status = JobStatus.from_dict(json.loads(status_json))

                if (
                    job_status.status not in WAITING_STATUS
                    or job_status.status == wait_for_status
                ):
                    break
            break
        except ConnectionClosedError:
            # logger.debug(
            #     "Websocket connection closed... attempting to reconnect..."
            # )
            continue
        finally:
            try:
                await websocket.close()
            except GeneratorExit:
                pass

    return job_status
