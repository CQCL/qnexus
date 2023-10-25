from pydantic import BaseModel
from typing import Optional


class Meta(BaseModel):
    page_number: Optional[int] = None
    page_size: Optional[int] = None
    total_pages: Optional[int] = None
    total_count: Optional[int] = None
