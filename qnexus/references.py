from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from pytket.backends.status import StatusEnum

from qnexus.annotations import Annotations


class BaseRef(BaseModel):
    model_config = ConfigDict(frozen=True)


class ProjectRef(BaseRef):
    id: UUID
    annotations: Annotations


class CircuitRef(BaseRef):
    id: UUID
    annotations: Annotations
    project: ProjectRef

class JobType(str, Enum):
    Execute = "PROCESS"
    Compile = "COMPILE"

class JobRef(BaseRef):
    id: UUID
    annotations: Annotations
    job_type: JobType
    last_status: StatusEnum
    last_message: str
    project: ProjectRef
