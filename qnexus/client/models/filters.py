from datetime import datetime, timezone
from typing import Annotated, Literal, NotRequired, TypedDict, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from qnexus.client.models.utils import AllowNone
from qnexus.references import ProjectRef


class PropertiesFilterDict(TypedDict):
    """Resource time filters model."""

    properties: NotRequired[list[str]]


class PropertiesFilter(BaseModel):
    """Resource time filters model."""

    properties: list[str] = Field(
        default=[],
        serialization_alias="filter[properties]",
        description="Filter by resource label value.",
    )


class TimeFilterDict(TypedDict):
    """Resource time filters model."""

    created_before: NotRequired[datetime]
    created_after: NotRequired[datetime]
    modified_before: NotRequired[datetime]
    modified_after: NotRequired[datetime]


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


class PaginationFilterDict(TypedDict):
    """Pagination model."""

    page_number: NotRequired[int]
    page_size: NotRequired[int]


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


class CreatorFilterDict(TypedDict):
    """Creator email model."""

    creator_email: NotRequired[list[str]]


class CreatorFilter(BaseModel):
    """Creator email model."""

    creator_email: list[str] = Field(
        default=[],
        serialization_alias="filter[creator][email]",
        examples=["user@domain.com"],
        description="Filter by creator email.",
    )


class NameFilterDict(TypedDict):
    """Name model."""

    name: NotRequired[str]


class NameFilter(BaseModel):
    """Name model."""

    name: str = Field(
        default="",
        serialization_alias="filter[name]",
        description="Filter by name, fuzzy search.",
    )


class SortFilterDict(TypedDict):
    """Resource sorting model."""

    sort: NotRequired[
        list[
            Union[
                Literal["timestamps.created"],
                Literal["-timestamps.created"],
                Literal["timestamps.modified"],
                Literal["-timestamps.modified"],
                Literal["name"],
                Literal["-name"],
            ]
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


class ProjectIDFilterDict(TypedDict):
    """ProjectRef filter (TypedDict)"""

    project_id: NotRequired[str | UUID]


class ProjectRefFilter(BaseModel):
    """Project Id filter"""

    project_ref: Annotated[ProjectRef, AllowNone] = Field(
        default=None,
        serialization_alias="filter[project][id]",
        description="Filter by project ref",
    )

    @field_serializer("project_ref")
    def serialize_project_ref(self, project_ref: ProjectRef):
        return project_ref.id


class ProjectRefFilterDict(TypedDict):
    """ProjectRef filter (TypedDict)"""

    project_ref: NotRequired[ProjectRef]
