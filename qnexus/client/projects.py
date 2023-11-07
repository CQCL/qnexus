from .client import nexus_client
from pydantic import Field
import pandas as pd
from typing_extensions import Unpack, NotRequired
from .utils import normalize_included
from halo import Halo
from ..exceptions import ResourceFetchFailed
from .models.filters import (
    SortFilter,
    SortFilterDict,
    PaginationFilter,
    PaginationFilterDict,
    NameFilter,
    NameFilterDict,
    CreatorFilter,
    CreatorFilterDict,
    PropertiesFilter,
    PropertiesFilterDict,
    TimeFilter,
    TimeFilterDict,
)


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

    pass
    archived: NotRequired[bool]


@Halo(text="Listing projects...", spinner="simpleDotsScrolling")
def projects(**kwargs: Unpack[ParamsDict]):
    """
    List projects you have access to.

    Examples
    --------
    Listed projects can be filtered:

    >>> projects = qnx.projects.list(
        is_archived=False,
        sort=["-name"]
    )
    ...
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

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    included_map = normalize_included(res.json()["included"])

    formatted_projects = [
        {
            "Name": project["attributes"]["name"],
            "Created by": included_map[
                project["relationships"]["creator"]["data"]["type"]
            ][project["relationships"]["creator"]["data"]["id"]]["attributes"][
                "display_name"
            ],
            "Created": project["attributes"]["timestamps"]["created"],
            "Description": (project["attributes"]["description"] or "-"),
            "Archived": True if project["attributes"]["archived"] else False,
            "Properties": project["attributes"]["properties"],
        }
        for project in res.json()["data"]
    ]

    print(pd.DataFrame.from_records(formatted_projects))
