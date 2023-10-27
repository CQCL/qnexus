from pydantic import Field, BaseModel
from typing import Optional, Union, Literal, TypedDict, List
from typing_extensions import NotRequired


class PropertiesFilterDict(TypedDict):
    """Resource time filters model."""

    properties: NotRequired[list[str]]


class PropertiesFilter(BaseModel):
    """Resource time filters model."""

    properties: list[str] = Field(
        default=None, serialization_alias="filter[properties]"
    )


class TimeFilterDict(TypedDict):
    """Resource time filters model."""

    created_before: NotRequired[str]
    created_after: NotRequired[str]
    modified_before: NotRequired[str]
    modified_after: NotRequired[str]


class TimeFilter(BaseModel):
    """Resource time filters model."""

    created_before: Optional[str] = Field(
        default=None,
        serialization_alias="filter[timestamps][created][before]",
    )
    created_after: Optional[str] = Field(
        default=None, serialization_alias="filter[timestamps][created][after]"
    )
    modified_before: Optional[str] = Field(
        default=None, serialization_alias="filter[timestamps][modified][before]"
    )
    modified_after: Optional[str] = Field(
        default=None, serialization_alias="filter[timestamps][modified][after]"
    )


class PaginationFilterDict(TypedDict):
    """Pagination model."""

    page_number: NotRequired[int]
    page_size: NotRequired[int]


class PaginationFilter(BaseModel):
    """Pagination model."""

    page_number: Optional[int] = Field(default=None, serialization_alias="page[number]")
    page_size: Optional[int] = Field(default=None, serialization_alias="page[size]")


class CreatorFilterDict(TypedDict):
    """Creator email model."""

    creator_email: NotRequired[list[str]]


class CreatorFilter(BaseModel):
    """Creator email model."""

    creator_email: list[str] = Field(
        default=[], serialization_alias="filter[creator][email]"
    )


class NameFilterDict(TypedDict):
    """Name model."""

    name: NotRequired[str]


class NameFilter(BaseModel):
    """Name model."""

    name: Optional[str] = Field(default=None, serialization_alias="filter[name]")


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

    sort: Optional[
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
    ] = ["-timestamps.created"]
