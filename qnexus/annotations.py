from collections import OrderedDict
from typing import NotRequired, TypedDict

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator

PropertiesDict = OrderedDict[str, bool | int | float | str]


class AnnotationsDict(TypedDict):
    name: NotRequired[str | None]
    description: NotRequired[str | None]
    properties: NotRequired[PropertiesDict]


class Annotations(BaseModel):
    name: str | None = None
    description: str | None = None
    properties: PropertiesDict = Field(default_factory=OrderedDict)

    model_config = ConfigDict(frozen=True)

    @field_validator("properties")
    def sort_properties(cls, v: dict):
        """Sort the values of"""
        return OrderedDict(sorted(v.items()))

    def summarize(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(
            {"name": self.name, "description": self.description} | self.properties,
            index=[0],
        )


class CreateAnnotationsDict(AnnotationsDict):
    # Name is no longer optional
    name: str


class CreateAnnotations(Annotations):
    # Name is no longer optional
    name: str
