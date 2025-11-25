from datetime import datetime
from typing import Literal
from uuid import UUID

import pandas as pd
from pydantic import Field, field_serializer

from qnexus.models.annotations import Annotations
from qnexus.models.references.base import BaseRef


class ProjectRef(BaseRef):
    """Proxy object to a Project in Nexus."""

    annotations: Annotations
    contents_modified: datetime
    archived: bool = Field(default=False)
    id: UUID
    type: Literal["ProjectRef"] = "ProjectRef"

    @field_serializer("contents_modified")
    def serialize_modified(self, contents_modified: datetime | None) -> str | None:
        """Custom serializer for datetimes."""
        if contents_modified:
            return str(contents_modified)
        return None

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame(
            {
                "name": self.annotations.name,
                "description": self.annotations.description,
                "created": self.annotations.created,
                "modified": self.annotations.modified,
                "contents_modified": self.contents_modified,
                "archived": self.archived,
                "id": self.id,
            },
            index=[0],
        )
