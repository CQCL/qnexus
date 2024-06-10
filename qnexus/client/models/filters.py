"""Filter models for use by the client."""
from datetime import datetime
from typing import Annotated, Literal, OrderedDict, TypedDict, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from qnexus.client.models.annotations import PropertiesDict
from qnexus.client.models.utils import AllowNone
from qnexus.references import ProjectRef


class PropertiesFilterDict(TypedDict, total=False):
    """Properties filters model."""

    properties: PropertiesDict


def _format_property(key: str, value: bool | int | float | str) -> str:
    if isinstance(value, str):
        return f"({key},'{value}')"
    return f"({key},{value})"


class PropertiesFilter(BaseModel):
    """Properties filters model."""

    properties: PropertiesDict = Field(
        default=OrderedDict(),
        serialization_alias="filter[properties]",
        description="Filter by resource label value.",
    )

    @field_serializer("properties")
    def serialize_properties(self, properties: PropertiesDict):
        """Serialize the id for a ProjectRef."""
        return [_format_property(key, value) for key, value in properties.items()]


class TimeFilterDict(TypedDict, total=False):
    """Resource time filters model."""

    created_before: datetime
    created_after: datetime
    modified_before: datetime
    modified_after: datetime


class TimeFilter(BaseModel):
    """Resource time filters model."""

    created_before: Annotated[datetime, AllowNone] = Field(
        default=None,
        serialization_alias="filter[timestamps][created][before]",
        description="Show items created before this date.",
    )
    created_after: Annotated[datetime, AllowNone] = Field(
        default=None,
        serialization_alias="filter[timestamps][created][after]",
        description="Show items created after this date.",
    )
    modified_before: Annotated[datetime, AllowNone] = Field(
        default=None,
        serialization_alias="filter[timestamps][modified][before]",
        description="Show items modified before this date.",
    )
    modified_after: Annotated[datetime, AllowNone] = Field(
        default=None,
        serialization_alias="filter[timestamps][modified][after]",
        description="Show items modified after this date.",
    )


class PaginationFilterDict(TypedDict, total=False):
    """Pagination model."""

    page_number: int
    page_size: int


class PaginationFilter(BaseModel):
    """Pagination model."""

    page_number: int = Field(
        default=0,
        serialization_alias="page[number]",
        description="Specific page to return.",
    )
    page_size: int = Field(
        default=50,
        serialization_alias="page[size]",
        description="Size of page that is returned.",
    )


class CreatorFilterDict(TypedDict, total=False):
    """Creator email model."""

    creator_email: list[str]


class CreatorFilter(BaseModel):
    """Creator email model."""

    creator_email: list[str] = Field(
        default=[],
        serialization_alias="filter[creator][email]",
        examples=["user@domain.com"],
        description="Filter by creator email.",
    )


class FuzzyNameFilterDict(TypedDict, total=False):
    """Name model."""

    name_like: str


class FuzzyNameFilter(BaseModel):
    """Name model."""

    name_like: str = Field(
        default="",
        serialization_alias="filter[name]",
        description="Filter by name, fuzzy search.",
    )


class SortFilterDict(TypedDict, total=False):
    """Resource sorting model."""

    sort: list[
        Union[
            Literal["timestamps.created"],
            Literal["-timestamps.created"],
            Literal["timestamps.modified"],
            Literal["-timestamps.modified"],
            Literal["name"],
            Literal["-name"],
        ]
    ]


class SortFilter(BaseModel):
    """Resource sorting model."""

    sort: list[
        Union[
            Literal["timestamps.created"],
            Literal["-timestamps.created"],
            Literal["timestamps.modified"],
            Literal["-timestamps.modified"],
            Literal["name"],
            Literal["-name"],
        ]
    ] = Field(
        default=["-timestamps.created"],
        serialization_alias="sort",
        description="Sort items.",
    )


class ProjectIDFilter(BaseModel):
    """Project Id filter"""

    project_id: Annotated[str | UUID, AllowNone] = Field(
        default=None,
        serialization_alias="filter[project][id]",
        description="Filter by project id",
    )


class ProjectIDFilterDict(TypedDict, total=False):
    """ProjectRef filter (TypedDict)"""

    project_id: str | UUID


class ProjectRefFilter(BaseModel):
    """Project Id filter"""

    project_ref: Annotated[ProjectRef, AllowNone] = Field(
        default=None,
        serialization_alias="filter[project][id]",
        description="Filter by project ref",
    )

    @field_serializer("project_ref")
    def serialize_project_ref(self, project_ref: ProjectRef):
        """Serialize the id for a ProjectRef."""
        return project_ref.id


class ProjectRefFilterDict(TypedDict, total=False):
    """ProjectRef filter (TypedDict)"""

    project_ref: ProjectRef


class ArchivedFilter(BaseModel):
    """Include or omit archived projects"""

    is_archived: Annotated[bool, AllowNone] = Field(
        default=False,
        serialization_alias="filter[archived]",
        description="Include or omit archived projects",
    )


class ArchivedFilterDict(TypedDict, total=False):
    """Include or omit archived projects (TypedDict)"""

    is_archived: bool
