from .client import nexus_client
from pydantic import Field, BaseModel
from colorama import Fore, Style
import pandas as pd
from typing import TypedDict, Union, List, Optional, Annotated
from typing_extensions import Unpack, TypedDict, Literal, NotRequired
from .models.utils import AllowNone

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

    archived: Annotated[bool, AllowNone] = Field(
        default=None,
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
    pass
    archived: NotRequired[bool]


#
def list(**kwargs: Unpack[ParamsDict]):
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

    params = Params(**kwargs).model_dump(by_alias=True, exclude_none=True)
    print("Fetching projects...")
    res = nexus_client.get(
        "/api/projects/v1beta",
        params=params,
    )

    formatted_projects = [
        {
            "Name": project["attributes"]["name"],
            "Created by": "Somebody",
            "Description": (project["attributes"]["description"] or "-"),
            "Archived": True if project["attributes"]["archived"] else False,
            "Properties": project["attributes"]["properties"],
        }
        for project in res.json()["data"]
    ]

    return pd.DataFrame.from_records(formatted_projects)
