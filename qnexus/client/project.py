"""Client API for projects in Nexus."""
# pylint: disable=redefined-builtin
import random
from typing import Any, Literal, Union
from uuid import UUID

from typing_extensions import Unpack

# from halo import Halo
import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.database_iterator import DatabaseIterator
from qnexus.client.models.annotations import (
    Annotations,
    CreateAnnotations,
    CreateAnnotationsDict,
)
from qnexus.client.models.filters import (
    ArchivedFilter,
    ArchivedFilterDict,
    CreatorFilter,
    CreatorFilterDict,
    FuzzyNameFilter,
    FuzzyNameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    PropertiesFilter,
    PropertiesFilterDict,
    SortFilter,
    SortFilterDict,
    TimeFilter,
    TimeFilterDict,
)
from qnexus.client.utils import handle_fetch_errors
from qnexus.context import get_active_project
from qnexus.client.models import Property
from qnexus.references import DataframableList, ProjectRef

# Colour-blind friendly colours from https://www.nature.com/articles/nmeth.1618
_COLOURS = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7"]


class Params(
    SortFilter,
    PaginationFilter,
    FuzzyNameFilter,
    CreatorFilter,
    PropertiesFilter,
    TimeFilter,
    ArchivedFilter,
):
    """Params for filtering projects"""


class ParamsDict(
    PaginationFilterDict,
    FuzzyNameFilterDict,
    CreatorFilterDict,
    PropertiesFilterDict,
    TimeFilterDict,
    SortFilterDict,
    ArchivedFilterDict,
):
    """Params for filtering projects (TypedDict)"""


# @Halo(text="Listing projects...", spinner="simpleDotsScrolling")
def get(**kwargs: Unpack[ParamsDict]) -> DatabaseIterator[ProjectRef]:
    """Get a DatabaseIterator over projects with optional filters."""

    params = Params(**kwargs).model_dump(
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )

    return DatabaseIterator(
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


def get_only(
    id: Union[str, UUID, None] = None, **kwargs: Unpack[ParamsDict]
) -> ProjectRef:
    """Attempt to get an exact match on a project by using filters
    that uniquely identify one."""
    if id:
        return _fetch(id)

    return get(**kwargs).try_unique_match()


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


def create(**kwargs: Unpack[CreateAnnotationsDict]) -> ProjectRef:
    """Create a new project in Nexus."""
    attributes = {}
    annotations = CreateAnnotations(**kwargs).model_dump(exclude_none=True)
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
    project_ref: ProjectRef | None = None,
    description: str | None = None,
    required: bool = False,
) -> None:
    """Add a property definition to a project."""
    project_ref = project_ref or get_active_project(project_required=True)
    assert project_ref, "ProjectRef required."

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
                "project": {"data": {"id": str(project_ref.id), "type": "project"}}
            },
            "type": "property",
        }
    }
    props_res = nexus_client.post(
        "/api/property_definitions/v1beta", json=props_req_dict
    )

    if props_res.status_code != 200:
        raise qnx_exc.ResourceCreateFailed(
            message=props_res.json(), status_code=props_res.status_code
        )


def get_properties(project: ProjectRef | None = None) -> DataframableList[Property]:
    """Get the property definitions for the Project."""
    # This will get all the properties (even if there are more than the page size),
    # but could be refactored if needed.

    project = project or get_active_project(project_required=True)
    assert project, "ProjectRef required."

    all_project_properties_iterator = DatabaseIterator(
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
