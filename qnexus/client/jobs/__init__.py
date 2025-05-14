"""Client API for jobs in Nexus."""

import asyncio
import json
import ssl
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Type, Union, cast, overload
from uuid import UUID

from pytket.backends.status import WAITING_STATUS, StatusEnum
from quantinuum_schemas.models.backend_config import config_name_to_class
from quantinuum_schemas.models.hypertket_config import HyperTketConfig
from websockets.client import connect
from websockets.exceptions import ConnectionClosed

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.client.jobs import _compile, _execute
from qnexus.client.nexus_iterator import NexusIterator
from qnexus.client.utils import handle_fetch_errors
from qnexus.config import CONFIG
from qnexus.context import (
    get_active_project,
    merge_project_from_context,
    merge_properties_from_context,
)
from qnexus.models import BackendConfig
from qnexus.models.annotations import Annotations, PropertiesDict
from qnexus.models.filters import (
    CreatorFilter,
    FuzzyNameFilter,
    JobStatusEnum,
    JobStatusFilter,
    JobTypeFilter,
    PaginationFilter,
    ProjectRefFilter,
    PropertiesFilter,
    ScopeFilter,
    ScopeFilterEnum,
    SortFilter,
    SortFilterEnum,
    TimeFilter,
)
from qnexus.models.job_status import JobStatus
from qnexus.models.language import Language
from qnexus.models.references import (
    CircuitRef,
    CompilationResultRef,
    CompileJobRef,
    DataframableList,
    ExecuteJobRef,
    ExecutionProgram,
    ExecutionResult,
    ExecutionResultRef,
    JobRef,
    JobType,
    ProjectRef,
    WasmModuleRef,
)
from qnexus.models.utils import assert_never

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


class Params(
    CreatorFilter,
    PropertiesFilter,
    PaginationFilter,
    FuzzyNameFilter,
    JobStatusFilter,
    ProjectRefFilter,
    JobTypeFilter,
    ScopeFilter,
    SortFilter,
    TimeFilter,
):
    """Params for filtering jobs"""


@merge_project_from_context
def get_all(
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    job_status: list[JobStatusEnum] | None = None,
    job_type: list[JobType] | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    scope: ScopeFilterEnum | None = None,
) -> NexusIterator[CompileJobRef | ExecuteJobRef]:
    """Get a NexusIterator over jobs with optional filters."""
    project = project or get_active_project(project_required=False)
    project = cast(ProjectRef, project)

    params = Params(
        name_like=name_like,
        creator_email=creator_email,
        project=project,
        status=(
            JobStatusFilter.convert_status_filters(job_status) if job_status else None
        ),
        job_type=job_type,
        properties=properties,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        sort=SortFilter.convert_sort_filters(sort_filters),
        page_number=page_number,
        page_size=page_size,
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    return NexusIterator(
        resource_type="Job",
        nexus_url="/api/jobs/v1beta2",
        params=params,
        wrapper_method=_to_jobref,
        nexus_client=get_nexus_client(),
    )


def _to_jobref(data: dict[str, Any]) -> DataframableList[CompileJobRef | ExecuteJobRef]:
    """Parse a json dictionary into a list of JobRefs."""

    job_list: list[CompileJobRef | ExecuteJobRef] = []

    for entry in data["data"]:
        project_id = entry["relationships"]["project"]["data"]["id"]
        project_details = next(
            proj for proj in data["included"] if proj["id"] == project_id
        )
        project = ProjectRef(
            id=project_id,
            annotations=Annotations.from_dict(project_details["attributes"]),
            contents_modified=project_details["attributes"]["contents_modified"],
            archived=project_details["attributes"]["archived"],
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
                project=project,
            )
        )
    return DataframableList(job_list)


def get(
    id: Union[str, UUID, None] = None,
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    job_status: list[JobStatusEnum] | None = None,
    job_type: list[JobType] | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    scope: ScopeFilterEnum | None = None,
) -> JobRef:
    """
    Get a single job using filters. Throws an exception if the filters do
    not match exactly one object.
    """
    if id:
        return _fetch_by_id(job_id=id, scope=scope)

    return get_all(
        name_like=name_like,
        creator_email=creator_email,
        project=project,
        properties=properties,
        job_status=job_status,
        job_type=job_type,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        sort_filters=sort_filters,
        page_number=page_number,
        page_size=page_size,
        scope=scope,
    ).try_unique_match()


def _fetch_by_id(job_id: UUID | str, scope: ScopeFilterEnum | None) -> JobRef:
    """Utility method for fetching directly by a unique identifier."""
    params = Params(
        scope=scope,
    ).model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

    res = get_nexus_client().get(f"/api/jobs/v1beta2/{job_id}", params=params)

    handle_fetch_errors(res)

    job_data = res.json()

    project_id = job_data["data"]["relationships"]["project"]["data"]["id"]
    project_details = next(
        proj for proj in job_data["included"] if proj["id"] == project_id
    )
    project = ProjectRef(
        id=project_id,
        annotations=Annotations.from_dict(project_details["attributes"]),
        contents_modified=project_details["attributes"]["contents_modified"],
        archived=project_details["attributes"]["archived"],
    )
    job_type: Type[CompileJobRef] | Type[ExecuteJobRef]
    match job_data["data"]["attributes"]["job_type"]:
        case JobType.COMPILE:
            job_type = CompileJobRef
        case JobType.EXECUTE:
            job_type = ExecuteJobRef
        case _:
            assert_never(job_data["attributes"]["job_type"])

    backend_config_dict = job_data["data"]["attributes"]["definition"]["backend_config"]
    backend_config_class = config_name_to_class[backend_config_dict["type"]]
    backend_config: BackendConfig = backend_config_class(  # type: ignore
        **backend_config_dict
    )

    return job_type(
        id=job_data["data"]["id"],
        annotations=Annotations.from_dict(job_data["data"]["attributes"]),
        job_type=job_data["data"]["attributes"]["job_type"],
        last_status=JobStatus.from_dict(
            job_data["data"]["attributes"]["status"]
        ).status,
        last_message=JobStatus.from_dict(
            job_data["data"]["attributes"]["status"]
        ).message,
        project=project,
        backend_config_store=backend_config,
    )


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
    resp = get_nexus_client().get(f"api/jobs/v1beta2/{job.id}/attributes/status")
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
    if not CONFIG.httpx_verify:
        ssl_reconfigured = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_reconfigured.check_hostname = False
        ssl_reconfigured.verify_mode = ssl.CERT_NONE

    extra_headers = {
        # TODO, this cookie will expire frequently
        "Cookie": f"myqos_id={get_nexus_client().auth.cookies.get('myqos_id')}"  # type: ignore
    }
    async for websocket in connect(
        f"{CONFIG.websockets_url}/api/jobs/v1beta2/{job.id}/attributes/status/ws",
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
        except ConnectionClosed:
            # logger.debug(
            #     "Websocket connection closed... attempting to reconnect..."
            # )
            continue
        finally:
            try:
                await websocket.close(code=1000, reason="Client closed connection")
            except GeneratorExit:
                pass

    return job_status


@overload
def results(
    job: CompileJobRef, allow_incomplete: bool = False
) -> DataframableList[CompilationResultRef]: ...


@overload
def results(
    job: ExecuteJobRef, allow_incomplete: bool = False
) -> DataframableList[ExecutionResultRef]: ...


def results(
    job: CompileJobRef | ExecuteJobRef,
    allow_incomplete: bool = False,
) -> DataframableList[CompilationResultRef] | DataframableList[ExecutionResultRef]:
    """Get the ResultRefs from a JobRef, if the job is complete.
    To enable fetching results from Jobs with incomplete items, set allow_incomplete=True.
    """
    match job:
        case CompileJobRef():
            return _compile._results(job, allow_incomplete)
        case ExecuteJobRef():
            return _execute._results(job, allow_incomplete)
        case _:
            assert_never(job.job_type)


def retry_submission(
    job: JobRef,
    retry_status: list[StatusEnum] | None = None,
    remote_retry_strategy: RemoteRetryStrategy = RemoteRetryStrategy.DEFAULT,
    user_group: str | None = None,
) -> None:
    """Retry a job in Nexus according to status(es) or retry strategy.

    By default, jobs with the ERROR status will be retried.
    """
    body: dict[str, str | list[str]] = {"remote_retry_strategy": remote_retry_strategy}

    if user_group is not None:
        body["user_group"] = user_group

    if retry_status is not None:
        body["retry_status"] = [status.name for status in retry_status]

    res = get_nexus_client().post(
        f"/api/jobs/v1beta2/{job.id}/rpc/retry",
        json=body,
    )
    if res.status_code != 202:
        res.raise_for_status()


def cancel(job: JobRef) -> None:
    """Attempt cancellation of a job in Nexus.

    If the job has been submitted to a backend, Nexus will request cancellation of the job.
    """
    res = get_nexus_client().post(
        f"/api/jobs/v1beta2/{job.id}/rpc/cancel",
        json={},
    )

    if res.status_code != 202:
        res.raise_for_status()


def delete(job: JobRef) -> None:
    """Delete a job in Nexus."""
    res = get_nexus_client().delete(
        f"/api/jobs/v1beta/{job.id}",
    )

    if res.status_code != 204:
        res.raise_for_status()


@merge_properties_from_context
def compile(
    circuits: Union[CircuitRef, list[CircuitRef]],
    backend_config: BackendConfig,
    name: str,
    description: str = "",
    project: ProjectRef | None = None,
    properties: PropertiesDict | None = None,
    optimisation_level: int = 2,
    credential_name: str | None = None,
    user_group: str | None = None,
    hypertket_config: HyperTketConfig | None = None,
    timeout: float | None = 300.0,
) -> DataframableList[CircuitRef]:
    """
    Utility method to run a compile job on a circuit or circuits and return a
    DataframableList of the compiled circuits.
    """
    project = project or get_active_project(project_required=True)
    project = cast(ProjectRef, project)

    compile_job_ref = _compile.start_compile_job(
        circuits=circuits,
        backend_config=backend_config,
        name=name,
        description=description,
        project=project,
        properties=properties,
        optimisation_level=optimisation_level,
        credential_name=credential_name,
        user_group=user_group,
        hypertket_config=hypertket_config,
    )

    wait_for(job=compile_job_ref, timeout=timeout)

    compile_results = results(compile_job_ref)

    return DataframableList(
        [compile_result.get_output() for compile_result in compile_results]
    )


@merge_properties_from_context
def execute(
    circuits: Union[ExecutionProgram, list[ExecutionProgram]],
    n_shots: list[int] | list[None],
    backend_config: BackendConfig,
    name: str,
    description: str = "",
    properties: PropertiesDict | None = None,
    project: ProjectRef | None = None,
    valid_check: bool = True,
    postprocess: bool = False,
    noisy_simulator: bool = True,
    wasm_module: WasmModuleRef | None = None,
    language: Language = Language.AUTO,
    seed: int | None = None,
    credential_name: str | None = None,
    user_group: str | None = None,
    timeout: float | None = 300.0,
) -> list[ExecutionResult]:
    """
    Utility method to run an execute job and return the results. Blocks until
    the results are available. See ``qnexus.start_execute_job`` for a function
    that submits the job and returns immediately, rather than waiting for
    results.
    """

    execute_job_ref = _execute.start_execute_job(
        circuits=circuits,
        n_shots=n_shots,
        backend_config=backend_config,
        name=name,
        description=description,
        properties=properties,
        project=project,
        valid_check=valid_check,
        postprocess=postprocess,
        noisy_simulator=noisy_simulator,
        wasm_module=wasm_module,
        language=language,
        seed=seed,
        credential_name=credential_name,
        user_group=user_group,
    )

    wait_for(job=execute_job_ref, timeout=timeout)

    execute_results = results(execute_job_ref)

    return [result.download_result() for result in execute_results]
