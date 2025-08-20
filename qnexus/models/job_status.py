"""Status types for Nexus Jobs."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, NamedTuple, Optional

import pandas as pd


class JobStatusEnum(str, Enum):
    """Possible job statuses"""

    COMPLETED = "COMPLETED"
    QUEUED = "QUEUED"
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    CANCELLING = "CANCELLING"
    RETRYING = "RETRYING"
    TERMINATED = "TERMINATED"
    DEPLETED = "DEPLETED"


class JobStatus(NamedTuple):
    """The status of a job along with an optional description.

    Optionally can also include extra fields such as:
    * Detailed error information.
    * Timestamps for changes in status.
    * Queue position.
    """

    status: JobStatusEnum
    message: str = ""
    error_detail: Optional[str] = None

    # Timestamp for when a status was last entered.
    completed_time: Optional[datetime] = None
    queued_time: Optional[datetime] = None
    submitted_time: Optional[datetime] = None
    running_time: Optional[datetime] = None
    cancelled_time: Optional[datetime] = None
    error_time: Optional[datetime] = None

    queue_position: Optional[int] = None

    @classmethod
    def from_dict(cls, dic: Dict[str, Any]) -> "JobStatus":
        """Construct from JSON serializable dictionary."""
        invalid = ValueError(f"Dictionary invalid format for JobStatus: {dic}")
        if "message" not in dic or "status" not in dic:
            raise invalid

        try:
            status = next(s for s in JobStatusEnum if dic["status"] == s.name)
        except StopIteration as err:
            raise invalid from err

        error_detail = dic.get("error_detail", None)

        def read_optional_datetime(key: str) -> datetime | None:
            x = dic.get(key)
            return datetime.fromisoformat(x) if x is not None else None

        completed_time = read_optional_datetime("completed_time")
        queued_time = read_optional_datetime("queued_time")
        submitted_time = read_optional_datetime("submitted_time")
        running_time = read_optional_datetime("running_time")
        cancelled_time = read_optional_datetime("cancelled_time")
        error_time = read_optional_datetime("error_time")

        queue_position = dic.get("queue_position", None)

        return cls(
            status,
            dic["message"],
            error_detail,
            completed_time,
            queued_time,
            submitted_time,
            running_time,
            cancelled_time,
            error_time,
            queue_position,
        )

    def df(self) -> pd.DataFrame:
        """Present in a pandas DataFrame."""
        return pd.DataFrame.from_dict(
            self._asdict(),
            orient="index",
        ).T


WAITING_STATUS = {JobStatusEnum.QUEUED, JobStatusEnum.SUBMITTED, JobStatusEnum.RUNNING}
