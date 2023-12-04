from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, TypedDict, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from typing_extensions import NotRequired, Unpack
from qnexus.annotations import Annotations

from qnexus.client.models.utils import AllowNone
from qnexus.references import JobRef, ProjectRef
from pytket.backends.status import CircuitStatus

from ..exceptions import ResourceCreateFailed, ResourceFetchFailed
from .client import nexus_client
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


#    meta = res.json()["meta"]
#    print("\n")
#    print(
#        f"Total jobs: {meta['total_count']}"
#        + " / "
#        + f"Page {meta['page_number']} of {meta['total_pages']}"
#        + " / "
#        + f"Page Size: {meta['page_size']}"
#    )
#    print(Fore.RESET)
#    formatted_jobs = [
#        {
#            "Name": job["name"],
#            "Job Type": "Execute"
#            if job["job_type"].title() == "Process"
#            else "Compile",
#            "Status": job["job_status"]["status"].title(),
#            "Message": job["job_status"]["message"],
#            "Project Id": job["experiment_id"],
#        }
#        for job in res.json()["data"]
#    ]
#
#    rich.print(pd.DataFrame.from_records(formatted_jobs))
