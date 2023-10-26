from .client import nexus_client
from typing import Optional
from pydantic import Field, TypeAdapter
from colorama import Fore

import pandas as pd
from .models.filters import (
    SortFilter,
    PaginationFilter,
    NameFilter,
    CreatorFilter,
    PropertiesFilter,
)


class Query(SortFilter, PaginationFilter, NameFilter, CreatorFilter, PropertiesFilter):
    """Query params for fetching projects"""

    is_archived: Optional[bool] = Field(
        default=None, serialization_alias="filter[archived]"
    )


def list(query: Optional[Query] = None):
    """List projects"""
    print("Fetching projects...")
    res = nexus_client.get(
        "/api/projects/v1beta", params=query.model_dump_json() if query else None
    ).json()
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
        for project in res["data"]
    ]
    return pd.DataFrame.from_records(formatted_projects)
