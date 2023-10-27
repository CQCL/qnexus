from .client import nexus_client

from pydantic import Field, BaseModel
from colorama import Fore
import pandas as pd
from typing import TypedDict, Union, List, Optional
from typing_extensions import Unpack, TypedDict, Literal, NotRequired

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

    is_archived: Optional[bool] = Field(
        default=None, serialization_alias="filter[archived]"
    )


class ParamsDict(
    SortFilterDict,
    PaginationFilterDict,
    NameFilterDict,
    CreatorFilterDict,
    PropertiesFilterDict,
    TimeFilterDict,
):
    pass


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
            "Name": Fore.YELLOW + project["attributes"]["name"],
            "Description": Fore.BLUE + (project["attributes"]["description"] or "-"),
            # "Created by": filter(
            #     lambda p: p["attributes"]["id"] == project["data"]["attributes"]["id"],
            #     res["included"],
            # )[0]["attributes"]["id"],
            "Archived": "🗃️" if project["attributes"]["archived"] else None,
            "Properties": project["attributes"]["properties"],
        }
        for project in res.json()["data"]
    ]

    return pd.DataFrame.from_records(formatted_projects)
