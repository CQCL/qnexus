from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseRef(BaseModel):
    """Base pydantic model."""

    model_config = ConfigDict(frozen=True)
    id: UUID
