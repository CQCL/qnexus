from pydantic import BaseModel, EmailStr
from typing import Optional, Union, Literal


class Sort(BaseModel):
    """Base sorting model."""

    sort: Union[
        Literal["timestamps.created"],
        Literal["-timestamps.created"],
        Literal["timestamps.modified"],
        Literal["-timestamps.modified"],
        Literal["name"],
        Literal["-name"],
    ] = Literal["-timestamps.created"]


class Pagination(BaseModel):
    """Base pagination model."""

    page_number: Optional[int] = None
    page_size: Optional[int] = None


#  'filter[submitted_before]':
#       'filter[submitted_after]':
#       'filter[timestamps][created][before]':
#       'filter[timestamps][modified][before]':
#       'filter[timestamps][created][after]':
#       'filter[timestamps][modified][after]':
class Time(BaseModel):
    submitted_before: Optional[str] = None
    submitted_after: Optional[str] = None
    created_before_: Optional[str] = None
    modified_before: Optional[str] = None
    created_after: Optional[str] = None
    modified_after: Optional[str] = None


class Filters(Pagination):
    """Filters available to all resources."""

    name: Optional[str] = None
    creator: Optional[EmailStr] = None
    is_archived: Optional[bool] = None
