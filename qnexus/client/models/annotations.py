"""The qnexus package."""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime
from typing import Any, NotRequired, TypedDict

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

PropertiesDict = OrderedDict[str, bool | int | float | str]


class AnnotationsDict(TypedDict):
    """TypedDict for annotations"""

    name: NotRequired[str | None]  # type: ignore
    description: NotRequired[str | None]
    properties: NotRequired[PropertiesDict]
    created: NotRequired[datetime | None]
    modified: NotRequired[datetime | None]


class Annotations(BaseModel):
    """Pydantic model for annotations"""

    name: str | None = None
    description: str | None = None
    properties: PropertiesDict = Field(default_factory=OrderedDict)
    created: datetime | None = None
    modified: datetime | None = None

    model_config = ConfigDict(frozen=True)

    @field_validator("properties")
    @classmethod
    def sort_properties(cls, v: dict):
        """Sort the values of"""
        return OrderedDict(sorted(v.items()))

    @field_serializer("created")
    def serialize_created(self, created: datetime | None, _info) -> str | None:
        """Custom serializer for datetimes."""
        if created:
            return str(created)
        return None

    @field_serializer("modified")
    def serialize_modified(self, modified: datetime | None, _info) -> str | None:
        """Custom serializer for datetimes."""
        if modified:
            return str(modified)
        return None

    def df(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.name,
                "description": self.description,
                "created": self.created,
                "modified": self.modified,
            }
            | self.properties,
            index=[0],
        )

    @classmethod
    def from_dict(cls, annotations_dict: dict[str, Any]) -> Annotations:
        """Construct Annotations from a dict."""
        return Annotations(
            name=annotations_dict["name"],
            description=annotations_dict.get("description", None),
            properties=PropertiesDict(**annotations_dict.get("properties", {})),
            created=annotations_dict["timestamps"]["created"],
            modified=annotations_dict["timestamps"]["modified"],
        )


class CreateAnnotationsDict(TypedDict):
    """TypedDict for annotations when the name is required."""

    name: str  # type: ignore
    description: NotRequired[str | None]
    properties: NotRequired[PropertiesDict]


class CreateAnnotations(BaseModel):
    """Pydantic model for annotations when the name is required."""

    name: str  # type: ignore
    description: str | None = None
    properties: PropertiesDict = Field(default_factory=OrderedDict)

    model_config = ConfigDict(frozen=True)
