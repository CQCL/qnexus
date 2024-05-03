"""Custom exceptions thrown in qnexus usage."""

from typing import Optional


class AuthenticationError(Exception):
    "Raised when there is an issue authenticating with the Nexus API."


class ResourceFetchFailed(Exception):
    """ResourceFetchFailed is an exception that occurs when a resource
    cannot be fetched from the platform to be read, or when expected data wasn't
    found on an object.
    """

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to fetch resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)


class ZeroMatches(Exception):
    """Zero Matches on a get call made to the Nexus database."""


class NoUniqueMatch(Exception):
    """No Unique Match on a get call made to the Nexus database."""


class JobError(Exception):
    """A Nexus Job has errored."""


class ResourceCreateFailed(Exception):
    """ResourceCreateFailed is an exception that occurs when a resource
    couldn't be created on the platform.
    """

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to create resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)


class ResourceUpdateFailed(Exception):
    """ResourceUpdateFailed is an exception that occurs when a resource
    cannot be updated on the platform.
    """

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to update resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)


class OptionalDependencyError(Exception):
    """Exception for import error"""

    def __init__(  # type: ignore
        self,
        *args,
        msg="An optional dependency is required for this action",
        **kwargs,
    ) -> None:
        super().__init__(*args, msg, **kwargs)
