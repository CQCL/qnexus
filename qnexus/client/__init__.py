from pydantic import BaseModel
from .health import *


class ResourceFilters(BaseModel):
    """Common resource filters."""


class ProcessJob(BaseModel):
    name: str


class ExecuteJob(BaseModel):
    name: str
