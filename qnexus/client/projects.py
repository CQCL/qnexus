"""Client API for projects in Nexus."""
# pylint: disable=redefined-builtin
import random
from datetime import datetime
from typing import Any, Literal, Union
from uuid import UUID

import pandas as pd

# from halo import Halo
import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.nexus_iterator import NexusIterator
from qnexus.client.utils import handle_fetch_errors
from qnexus.context import get_active_project
from qnexus.models import Property
from qnexus.models.annotations import Annotations, CreateAnnotations, PropertiesDict
from qnexus.models.filters import (  # PropertiesFilter, # Not yet implemented
    ArchivedFilter,
    CreatorFilter,
    FuzzyNameFilter,
    PaginationFilter,
    SortFilter,
    SortFilterEnum,
    TimeFilter,
)
from qnexus.models.references import DataframableList, ProjectRef

# Colour-blind friendly colours from https://www.nature.com/articles/nmeth.1618
_COLOURS = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7"]


class Params(
    SortFilter,
    PaginationFilter,
    FuzzyNameFilter,
    CreatorFilter,
    # PropertiesFilter, # Not yet implemented
    TimeFilter,
    ArchivedFilter,
):
    """Params for filtering projects"""


# @Halo(text="Listing projects...", spinner="simpleDotsScrolling")
def get_all(
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    is_archived: bool = False,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
) -> NexusIterator[ProjectRef]:
    """Get a NexusIterator over projects with optional filters."""

    params = Params(
        name_like=name_like,
        creator_email=creator_email,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        is_archived=is_archived,
        sort=SortFilter.convert_sort_filters(sort_filters),
        page_number=page_number,
        page_size=page_size,
    ).model_dump(
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )

    return NexusIterator(
        resource_type="Project",
        nexus_url="/api/projects/v1beta",
        params=params,
        wrapper_method=_to_projectref,
        nexus_client=nexus_client,
    )


def _to_projectref(data: dict[str, Any]) -> DataframableList[ProjectRef]:
    return DataframableList(
        [
            ProjectRef(
                id=project["id"],
                annotations=Annotations.from_dict(project["attributes"]),
                contents_modified=project["attributes"]["contents_modified"],
            )
            for project in data["data"]
        ]
    )


def get(
    *,
    id: Union[str, UUID, None] = None,
    name_like: str | None = None,
    creator_email: list[str] | None = None,
    created_before: datetime | None = None,
    created_after: datetime | None = datetime(day=1, month=1, year=2023),
    modified_before: datetime | None = None,
    modified_after: datetime | None = None,
    is_archived: bool = False,
    sort_filters: list[SortFilterEnum] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
) -> ProjectRef:
    """Attempt to get an exact match on a project by using filters
    that uniquely identify one."""
    if id:
        return _fetch(id)

    return get_all(
        name_like=name_like,
        creator_email=creator_email,
        created_before=created_before,
        created_after=created_after,
        modified_before=modified_before,
        modified_after=modified_after,
        is_archived=is_archived,
        sort_filters=sort_filters,
        page_number=page_number,
        page_size=page_size,
    ).try_unique_match()


def get_or_create(
    name: str,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> ProjectRef:
    """Get a project reference if the projects exists (by name),
    otherwise create a new project using the supplied description and properties."""
    annotations = CreateAnnotations(
        name=name,
        description=description,
        properties=properties,
    )
    try:
        return get(name_like=annotations.name)
    except qnx_exc.ZeroMatches:
        return create(
            name=annotations.name,
            description=annotations.description,
            properties=annotations.properties,
        )


def _fetch(project_id: UUID | str) -> ProjectRef:
    """Utility method for fetching directly by a unique identifier."""
    res = nexus_client.get(f"/api/projects/v1beta/{project_id}")

    handle_fetch_errors(res)

    res_dict = res.json()

    return ProjectRef(
        id=res_dict["data"]["id"],
        annotations=Annotations.from_dict(res_dict["data"]["attributes"]),
        contents_modified=res_dict["data"]["attributes"]["contents_modified"],
    )


def create(
    name: str,
    description: str | None = None,
    properties: PropertiesDict | None = None,
) -> ProjectRef:
    """Create a new project in Nexus."""
    attributes = {}
    annotations = CreateAnnotations(
        name=name,
        description=description,
        properties=properties,
    ).model_dump(exclude_none=True)
    attributes.update(annotations)

    req_dict = {
        "data": {
            "attributes": attributes,
            "relationships": {},
            "type": "project",
        }
    }

    res = nexus_client.post("/api/projects/v1beta", json=req_dict)

    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=res.json(), status_code=res.status_code
        )

    res_data_dict = res.json()["data"]

    return ProjectRef(
        id=UUID(res_data_dict["id"]),
        annotations=Annotations.from_dict(res_data_dict["attributes"]),
        contents_modified=res_data_dict["attributes"]["contents_modified"],
    )


def add_property(
    name: str,
    property_type: Literal["bool", "int", "float", "string"],
    project: ProjectRef | None = None,
    description: str | None = None,
    required: bool = False,
) -> None:
    """Add a property definition to a project."""
    project = project or get_active_project(project_required=True)
    assert project, "ProjectRef required."

    # For now required to add properties in a seperate API step
    props_req_dict = {
        "data": {
            "attributes": {
                "name": name,
                "description": description,
                "property_type": property_type,
                "required": required,
                "color": random.choice(_COLOURS),
            },
            "relationships": {
                "project": {"data": {"id": str(project.id), "type": "project"}}
            },
            "type": "property",
        }
    }
    props_res = nexus_client.post(
        "/api/property_definitions/v1beta", json=props_req_dict
    )

    if props_res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=props_res.json(), status_code=props_res.status_code
        )


def get_properties(project: ProjectRef | None = None) -> DataframableList[Property]:
    """Get the property definitions for the Project."""
    # This will get all the properties (even if there are more than the page size),
    # but could be refactored if needed.

    project = project or get_active_project(project_required=True)
    assert project, "ProjectRef required."

    all_project_properties_iterator = NexusIterator(
        resource_type="Property",
        nexus_url="/api/property_definitions/v1beta",
        params={"filter[project][id]": str(project.id)},
        wrapper_method=_to_property,
        nexus_client=nexus_client,
    )

    return all_project_properties_iterator.list()


def _to_property(data: dict[str, Any]) -> DataframableList[Property]:
    return DataframableList(
        [
            Property(
                annotations=Annotations.from_dict(property_dict["attributes"]),
                property_type=property_dict["attributes"]["property_type"],
                required=property_dict["attributes"]["required"],
                color=property_dict["attributes"]["color"],
                id=property_dict["id"],
            )
            for property_dict in data["data"]
        ]
    )


def summarize(project: ProjectRef) -> pd.DataFrame:
    """Summarize the current state of a project."""
    import qnexus.client.jobs as jobs_client  # pylint: disable=import-outside-toplevel

    all_jobs = jobs_client.get_all(project=project).list()

    return pd.DataFrame(
        {
            "project": project.annotations.name,
            "total_jobs": len(all_jobs),
            "pending_jobs": len(
                [
                    job
                    for job in all_jobs
                    if job.last_status in jobs_client.WAITING_STATUS
                ]
            ),
            "cancelled_jobs": len(
                [
                    job
                    for job in all_jobs
                    if job.last_status == jobs_client.StatusEnum.CANCELLED
                ]
            ),
            "errored_jobs": len(
                [
                    job
                    for job in all_jobs
                    if job.last_status == jobs_client.StatusEnum.ERROR
                ]
            ),
            "completed_jobs": len(
                [
                    job
                    for job in all_jobs
                    if job.last_status == jobs_client.StatusEnum.COMPLETED
                ]
            ),
        },
        index=[0],
    )
