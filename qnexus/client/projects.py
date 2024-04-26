import random
from typing import Any, Literal, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import NotRequired, Unpack

from qnexus.annotations import CreateAnnotations, CreateAnnotationsDict, Annotations
from qnexus.references import ProjectRef

# from halo import Halo
import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.models.filters import (
    CreatorFilter,
    CreatorFilterDict,
    NameFilter,
    NameFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    PropertiesFilter,
    PropertiesFilterDict,
    SortFilter,
    SortFilterDict,
    TimeFilter,
    TimeFilterDict,
)
from qnexus.client.utils import normalize_included

from qnexus.client.pagination_iterator import NexusDatabaseIterator
from qnexus.context import get_active_project


# Colour-blind friendly colours from https://www.nature.com/articles/nmeth.1618
_COLOURS = ["#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7"]


class Params(
    SortFilter,
    PaginationFilter,
    NameFilter,
    CreatorFilter,
    PropertiesFilter,
    TimeFilter,
):
    """Params for fetching projects"""

    archived: bool = Field(
        default=False,
        serialization_alias="filter[archived]",
        description="Include or omit archived projects",
    )


class ParamsDict(
    PaginationFilterDict,
    NameFilterDict,
    CreatorFilterDict,
    PropertiesFilterDict,
    TimeFilterDict,
    SortFilterDict,
):
    """Params for fetching projects (TypedDict)"""

    archived: NotRequired[bool]


# @Halo(text="Listing projects...", spinner="simpleDotsScrolling")
def filter(**kwargs: Unpack[ParamsDict]) -> NexusDatabaseIterator:
    """
    List projects you have access to.

    Examples
    --------
    Listed projects can be filtered:

    #>>> ps = projects.list(
    #...    is_archived=False,
    #...    sort=["-name"],
    #... )

    """

    params = Params(**kwargs).model_dump(
        by_alias=True,
        exclude_unset=True,
        exclude_none=True,
    )

    return NexusDatabaseIterator(
        resource_type="Project",
        nexus_url="/api/projects/v1beta",
        params=params,
        wrapper_method=_to_ProjectRef,
    )

    

def _to_ProjectRef(data: dict[str,Any]) -> list[ProjectRef]:
    return [ProjectRef(
            id=project["id"],
            annotations=Annotations(
                name=project["attributes"]["name"],
                description=project["attributes"].get("description", None),
                properties=project["attributes"]["properties"]
            )
        ) for project in data["data"]
    ]

def get(id: Union[str, UUID, None] = None, **kwargs: Unpack[ParamsDict]) -> ProjectRef:
    """ """
    if id:
        return _fetch(id)
    filter_call = filter(**kwargs)

    if filter_call.count() > 1:
        raise qnx_exc.NoUniqueMatch()
    if filter_call.count() == 0:
        raise qnx_exc.ZeroMatches()
    return filter_call.all()[0]


def _fetch(project_id: UUID | str) -> ProjectRef:
    """ """
    res = nexus_client.get(f"/api/projects/v1beta/{project_id}")

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches()

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    res_dict = res.json()

    return ProjectRef(
            id=res_dict["data"]["id"],
            annotations=Annotations(
                name=res_dict["data"]["attributes"]["name"],
                description=res_dict["data"]["attributes"].get("description", None),
                properties=res_dict["data"]["attributes"]["properties"]
            )
        )


def create(**kwargs: Unpack[CreateAnnotationsDict]) -> ProjectRef:
    attributes = {}
    annotations = CreateAnnotations(**kwargs).model_dump(exclude_none=True)
    attributes.update(annotations)
    relationships = {}

    req_dict = {
        "data": {
            "attributes": attributes,
            "relationships": relationships,
            "type": "project",
        }
    }

    res = nexus_client.post("/api/projects/v1beta", json=req_dict)

    if res.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(message=res.json(), status_code=res.status_code)
    
    res_data_dict = res.json()["data"]

    return ProjectRef(id=UUID(res_data_dict["id"]), annotations=annotations)

def add_property(
        name: str,
        property_type:  Literal["bool", "int", "float", "str"],
        project: ProjectRef | None = None,
        description: str | None = None,
        required: bool = False,
    ) -> None:
    """ """
    project = project or get_active_project(project_required=True)

    # For now required to add properties in a seperate API step
    props_req_dict = {
        "data": {
            "attributes": {
                "name": name,
                "description": description,
                "property_type": property_type,
                "required": required,
                "color":random.choice(_COLOURS) 
            },
            "relationships": {
                "project": {
                    "data": {
                        "id": str(project.id),
                        "type": "project"
                    }
                }
            },
            "type": "property",
        }
    }
    props_res = nexus_client.post("/api/property_definitions/v1beta", json=props_req_dict)

    if props_res.status_code != 200:
        raise qnx_exc.ResourceCreateFailed(message=props_res.json(), status_code=props_res.status_code)
