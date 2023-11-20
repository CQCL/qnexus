from typing import TypedDict

from pydantic import BaseModel, Field


class AnnotationsDict(TypedDict):
    name: str
    description: str | None
    properties: dict[str, bool | int | float | str]


class Annotations(BaseModel):
    name: str
    description: str | None = None
    properties: dict[str, bool | int | float | str] = Field(default_factory=dict)
