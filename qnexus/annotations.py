from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field


PropertiesDict = dict[str, bool | int | float | str]


class AnnotationsDict(TypedDict):
    name: str
    description: str | None
    properties: PropertiesDict


class Annotations(BaseModel):
    name: str
    description: str | None = None
    properties: PropertiesDict = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)
