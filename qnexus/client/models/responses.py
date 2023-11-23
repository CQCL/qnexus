from typing import Optional

from pydantic import BaseModel


class Meta(BaseModel):
    """Paginated meta model."""

    page_number: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_count: Optional[int] = None


class Attributes(BaseModel):
    """Attributes model"""

    class Timestamps(BaseModel):
        created: str
        modified: str

    timestamps = Timestamps
    name: str
    description: str
