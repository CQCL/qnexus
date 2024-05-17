"""Client API for jobs in Nexus."""
import asyncio
import json
import ssl
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, overload, TypedDict, Type, Union

from pydantic import BaseModel, ConfigDict, Field
from pytket.backends.status import WAITING_STATUS, StatusEnum
from typing_extensions import NotRequired, Unpack
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.database_iterator import DatabaseIterator
from qnexus.client.job import (
    compile as _compile,
    execute as _execute,
)  # pylint: disable=unused-import
from qnexus.client.models.annotations import Annotations
from qnexus.client.models.filters import (
    FuzzyNameFilter,
    FuzzyNameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    ProjectIDFilter,
    ProjectIDFilterDict,
    ProjectRefFilter,
    ProjectRefFilterDict,
)
from qnexus.client.models.job_status import JobStatus
from qnexus.client.models.utils import AllowNone, assert_never
from qnexus.config import Config
from qnexus.context import merge_project_from_context
from qnexus.references import (
    DataframableList,
    JobRef,
    JobType,
    ProjectRef,
    CompilationResultRef,
    ExecutionResultRef,
    ExecuteJobRef,
    CompileJobRef,
)

config = Config()

EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)


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
        default=[JobType.EXECUTE, JobType.COMPILE],
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
    # TODO add job id filter when availables
    PaginationFilter,
    FuzzyNameFilter,
    JobStatusFilter,
    ProjectIDFilter,
    ProjectRefFilter,
    JobTypeFilter,
):
    """Params for filtering jobs"""


class ParamsDict(
    PaginationFilterDict,
    FuzzyNameFilterDict,
    ProjectIDFilterDict,
    ProjectRefFilterDict,
    JobStatusFilterDict,
    JobTypeFilterDict,
):
    """Params for filtering jobs (TypedDict)"""


# @Halo(text="Listing jobs...", spinner="simpleDotsScrolling")
@merge_project_from_context
def get(
    **kwargs: Unpack[ParamsDict],
) -> DatabaseIterator[CompileJobRef | ExecuteJobRef]:
    """Get a DatabaseIterator over jobs with optional filters."""

    params = Params(**kwargs).model_dump(
        by_alias=True, exclude_unset=True, exclude_none=True, mode=""
    )
    if project_id_filter := params.pop("filter[project][id]", None):
        # TODO not needed after v1beta jobs api
        params["filter[experiment_id]"] = project_id_filter

    return DatabaseIterator(
        resource_type="Job",
        nexus_url="/api/v6/jobs",
        params=params,
        wrapper_method=_to_jobref,
        nexus_client=nexus_client,
    )


def _to_jobref(data: dict[str, Any]) -> DataframableList[CompileJobRef | ExecuteJobRef]:
    """Parse a json dictionary into a list of JobRefs."""

    job_list: list[CompileJobRef | ExecuteJobRef] = []

    for entry in data["data"]:
        job_type: Type[CompileJobRef] | Type[ExecuteJobRef]
        match entry["job_type"]:
            case JobType.COMPILE:
                job_type = CompileJobRef
            case JobType.EXECUTE:
                job_type = ExecuteJobRef
            case _:
                assert_never(entry["job_type"])

        job_list.append(
            # TODO fix this when v1beta jobs api is available
            job_type(
                id=entry["job_id"],
                annotations=Annotations(
                    name=entry["name"], created=EPOCH_START, modified=EPOCH_START
                ),
                job_type=entry["job_type"],
                last_status=JobStatus.from_dict(entry["job_status"]).status,
                last_message=JobStatus.from_dict(entry["job_status"]).message,
                project=ProjectRef(
                    id=entry["experiment_id"],
                    annotations=Annotations(
                        name="unimplemented", created=EPOCH_START, modified=EPOCH_START
                    ),
                    contents_modified=EPOCH_START,
                ),
            )
        )
    return DataframableList(job_list)


# id: Optional[str] = None,
def get_only(**kwargs: Unpack[ParamsDict]) -> JobRef:
    """Attempt to get an exact match on a job by using filters
    that uniquely identify one."""
    return get(**kwargs).try_unique_match()


def wait_for(
    job: JobRef,
    wait_for_status: StatusEnum = StatusEnum.COMPLETED,
    timeout: float | None = 300.0,
) -> JobStatus:
    """Check job status until the job is complete (or a specified status)."""
    job_status = asyncio.run(
        asyncio.wait_for(
            listen_job_status(job=job, wait_for_status=wait_for_status),
            timeout=timeout,
        )
    )

    if job_status.status == StatusEnum.ERROR:
        raise qnx_exc.JobError(f"Job errored with detail: {job_status.error_detail}")
    return job_status


def status(job: JobRef) -> JobStatus:
    """Get the status of a job."""
    resp = nexus_client.get(f"api/v6/jobs/{job.id}/status")
    if resp.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=resp.text, status_code=resp.status_code
        )
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


@overload
def results(job: CompileJobRef) -> DataframableList[CompilationResultRef]:
    ...


@overload
def results(job: ExecuteJobRef) -> DataframableList[ExecutionResultRef]:
    ...


def results(
    job: CompileJobRef | ExecuteJobRef,
) -> DataframableList[CompilationResultRef] | DataframableList[ExecutionResultRef]:
    """Get the ResultRefs from a JobRef, if the job is complete."""
    match job:
        case CompileJobRef():
            return _compile._results(job)  # pylint: disable=protected-access
        case ExecuteJobRef():
            return _execute._results(job)  # pylint: disable=protected-access
        case _:
            assert_never(job.job_type)


def retry_error(job: ExecuteJobRef):
    """Retry an errored execute job."""
    if job.job_type != JobType.EXECUTE:
        raise ValueError("Invalid job type")

    res = nexus_client.post(
        "/api/v6/jobs/process/retry_check", json={"job_id": str(job.id)}
    )

    if res.status_code != 202:
        res.raise_for_status()


def retry_submission(job: ExecuteJobRef):
    """Retry the submission of an execute job from Nexus to the target."""
    if job.job_type != JobType.EXECUTE:
        raise ValueError("Invalid job type")

    res = nexus_client.post(
        "/api/v6/jobs/process/retry_submit",
        json={"job_id": str(job.id), "resubmit_to_backend": True},
    )

    if res.status_code != 202:
        res.raise_for_status()
