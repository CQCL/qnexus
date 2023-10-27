from pydantic import Field, BaseModel
from typing import Optional, Union, Literal, TypedDict, List


class PropertiesFilter(BaseModel):
    """Resource time filters model."""

    properties: list[str] = Field(
        default=None, serialization_alias="filter[properties]"
    )


class TimeFilterDict(TypedDict):
    """Resource time filters model."""

    created_before: Optional[str]
    created_after: Optional[str]
    modified_before: Optional[str]
    modified_after: Optional[str]


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


class PaginationFilter(BaseModel):
    """Pagination model."""

    page_number: Optional[int] = Field(default=None, serialization_alias="page[number]")
    page_size: Optional[int] = Field(default=None, serialization_alias="page[size]")


class CreatorFilter(BaseModel):
    """Creator email model."""

    creator_email: list[str] = Field(
        default=[], serialization_alias="filter[creator][email]"
    )


class NameFilter(BaseModel):
    """Name model."""

    name: Optional[str] = Field(default=None, serialization_alias="filter[name]")


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
