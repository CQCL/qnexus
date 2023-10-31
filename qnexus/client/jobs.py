from .client import nexus_client
from pydantic import (
    Field,
    BaseModel,
    WrapValidator,
    ValidatorFunctionWrapHandler,
)
from colorama import Fore
import pandas as pd
from typing import Union, Annotated, TypedDict, Literal, Any
from typing_extensions import Unpack, NotRequired
from .models.filters import (
    PaginationFilter,
    PaginationFilterDict,
    NameFilter,
    NameFilterDict,
    ExperimentIDFilter,
    ExperimentIDFilterDict,
)
from halo import Halo


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


def parse_job_type(
    v: list[str], handler: ValidatorFunctionWrapHandler
) -> list[Union[Literal["PROCESS"], Literal["COMPILE"],]]:
    """Parse job type"""

    def parse_string(s: str):
        if s.upper() == "EXECUTE":
            return "PROCESS"
        if s.upper() == "COMPILE":
            return "COMPILE"
        raise Exception(f"Expected 'execute' or 'compile', received '{s}'.")

    return handler([parse_string(string) for string in v])


JobType = Annotated[list[str], WrapValidator(parse_job_type)]


class JobTypeFilter(BaseModel):
    """Filter by job type."""

    type: JobType = Field(
        default=["EXECUTE", "COMPILE"],
        serialization_alias="filter[job_type]",
        description="Filter by project_id",
    )


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


#
def list_jobs(**kwargs: Unpack[ParamsDict]):
    """
    List jobs.
    """
    params = Params(**kwargs).model_dump(by_alias=True, exclude_none=True, mode="")

    spinner = Halo(
        text="Fetching jobs...", color="blue", spinner="dots", animation="bounce"
    )
    spinner.start()

    res = nexus_client.get(
        "/api/v6/jobs",
        params=params,
    )

    meta = res.json()["meta"]
    print("\n")
    print(
        f"Total jobs: {meta['total_count']}"
        + " / "
        + f"Page {meta['page_number']} of {meta['total_pages']}"
        + " / "
        + Fore.BLUE
        + f"Page Size: {meta['page_size']}"
    )
    print(Fore.RESET)
    formatted_jobs = [
        {
            "Name": job["name"],
            "Job Type": "Execute"
            if job["job_type"].title() == "Process"
            else "Compile",
            "Status": job["job_status"]["status"].title(),
            "Project Id": job["experiment_id"],
            "Progress": "Unknown",
        }
        for job in res.json()["data"]
    ]

    print(pd.DataFrame.from_records(formatted_jobs))
    spinner.stop()
