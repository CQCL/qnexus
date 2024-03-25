import random
from typing import Literal
from uuid import UUID

import pandas as pd
from pydantic import Field
from typing_extensions import NotRequired, Unpack

from qnexus.annotations import Annotations, AnnotationsDict, PropertiesDict
from qnexus.references import ProjectRef

# from halo import Halo
from ..exceptions import ResourceCreateFailed, ResourceFetchFailed
from .client import nexus_client
from .models.filters import (
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
from .utils import normalize_included


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
def projects(**kwargs: Unpack[ParamsDict]) -> list[ProjectRef]:
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

    res = nexus_client.get(
        "/api/projects/v1beta",
        params=params,
    )

    if res.status_code >= 400:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    # included_map = normalize_included(res.json()["included"])

    # formatted_projects = [
    #     {
    #         "Identifier": project["id"],
    #         "Name": project["attributes"]["name"],
    #         "Created by": included_map[
    #             project["relationships"]["creator"]["data"]["type"]
    #         ][project["relationships"]["creator"]["data"]["id"]]["attributes"][
    #             "display_name"
    #         ],
    #         "Created": project["attributes"]["timestamps"]["created"],
    #         "Description": (project["attributes"]["description"] or "-"),
    #         "Archived": True if project["attributes"]["archived"] else False,
    #         "Properties": project["attributes"]["properties"],
    #     }
    #     for project in res.json()["data"]
    # ]

    return [
        ProjectRef(
            id=project["id"],
            annotations=Annotations(
                name=project["attributes"]["name"],
                description=project["attributes"].get("description", None),
                properties=project["attributes"]["properties"],
            ),
        )
        for project in res.json()["data"]
    ]


def submit(**kwargs: Unpack[AnnotationsDict]) -> ProjectRef:
    attributes = {}
    annotations = Annotations(**kwargs)
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

    if res.status_code >= 400:
        raise ResourceCreateFailed(message=res.json(), status_code=res.status_code)

    res_data_dict = res.json()["data"]

    return ProjectRef(id=UUID(res_data_dict["id"]), annotations=annotations)


def add_property(
    project: ProjectRef,
    name: str,
    property_type: Literal["bool", "int", "float", "str"],
    description: str | None = None,
    required: bool = True,
) -> None:
    """ """

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

    if props_res.status_code >= 400:
        raise ResourceCreateFailed(
            message=props_res.json(), status_code=props_res.status_code
        )
