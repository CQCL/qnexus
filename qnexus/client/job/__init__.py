"""Client API for jobs in Nexus."""
import asyncio
import json
from enum import Enum
import ssl
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Type, TypedDict, Union, overload

from pydantic import BaseModel, ConfigDict, Field
from pytket.backends.status import WAITING_STATUS, StatusEnum
from typing_extensions import Unpack
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.database_iterator import DatabaseIterator
from qnexus.client.job import compile as _compile  # pylint: disable=unused-import
from qnexus.client.job import execute as _execute
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
    CompilationResultRef,
    CompileJobRef,
    DataframableList,
    ExecuteJobRef,
    ExecutionResultRef,
    JobRef,
    JobType,
    ProjectRef,
)

config = Config()

EPOCH_START = datetime(1970, 1, 1, tzinfo=timezone.utc)


class RemoteRetryStrategy(str, Enum):
    """Strategy to use when retrying jobs.

    Each strategy defines how the system should approach resolving
    potential conflicts with remote state.

    DEFAULT will only attempt to re-sync status and collect results
    from the third party. Duplicate results will not be saved.

    ALLOW_RESUBMIT will submit the job to the third party again if
    # the system has no record of a third party handle.

    FORCE_RESUBMIT will submit the job to the third party again if
    the system has a job handle already but no result.

    FULL_RESTART will act as though the job is entirely fresh and
    re-perform every action.
    """

    DEFAULT = "DEFAULT"
    ALLOW_RESUBMIT = "ALLOW_RESUBMIT"
    FORCE_RESUBMIT = "FORCE_RESUBMIT"
    FULL_RESTART = "FULL_RESTART"


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


class JobStatusFilterDict(TypedDict, total=False):
    """Job status filter (TypedDict)"""

    status: list[
        Union[
            Literal["COMPLETED"],
            Literal["QUEUED"],
            Literal["SUBMITTED"],
            Literal["RUNNING"],
            Literal["CANCELLED"],
            Literal["ERROR"],
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


class JobTypeFilterDict(TypedDict, total=False):
    """Filter by job type (TypedDict)"""

    type: JobType
    submitted_after: datetime


class Params(
    # TODO add job id filter when available
    # TODO add job properties filter when available
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
        nexus_url="/api/jobs/v1beta",
        params=params,
        wrapper_method=_to_jobref,
        nexus_client=nexus_client,
    )


def _to_jobref(data: dict[str, Any]) -> DataframableList[CompileJobRef | ExecuteJobRef]:
    """Parse a json dictionary into a list of JobRefs."""

    job_list: list[CompileJobRef | ExecuteJobRef] = []

    for entry in data["data"]:
        project_id = entry["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in data["included"] if proj["id"] == project_id
        )
        project_ref = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
        )
        job_type: Type[CompileJobRef] | Type[ExecuteJobRef]
        match entry["attributes"]["job_type"]:
            case JobType.COMPILE:
                job_type = CompileJobRef
            case JobType.EXECUTE:
                job_type = ExecuteJobRef
            case _:
                assert_never(entry["attributes"]["job_type"])

        job_list.append(
            job_type(
                id=entry["id"],
                annotations=Annotations.from_dict(entry["attributes"]),
                job_type=entry["attributes"]["job_type"],
                last_status=JobStatus.from_dict(entry["attributes"]["status"]).status,
                last_message=JobStatus.from_dict(entry["attributes"]["status"]).message,
                project=project_ref,
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
    resp = nexus_client.get(f"api/jobs/v1beta/{job.id}/attributes/status")
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
        f"{config.websockets_url}/api/jobs/v1beta//{job.id}/attributes/status/ws",
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


def retry_submission(
    job: JobRef,
    retry_status: list[StatusEnum],
    remote_retry_strategy: RemoteRetryStrategy,
):
    """Retry a job in Nexus according to status(es) or retry strategy."""

    res = nexus_client.post(
        f"/api/jobs/v1beta/{job.id}/rpc/retry",
        json={
            "retry_status": retry_status,
            "remote_retry_strategy": remote_retry_strategy,
        },
    )
    if res.status_code != 202:
        res.raise_for_status()


def cancel(job: JobRef):
    """Attempt cancellation of a job in Nexus.

    If the job has been submitted to a backend, Nexus will request cancellation of the job.
    """
    res = nexus_client.post(
        f"/api/jobs/v1beta/{job.id}/rpc/cancel",
    )

    if res.status_code != 202:
        res.raise_for_status()
