"""Custom exceptions thrown in qnexus usage."""

from typing import Optional


class AuthenticationError(Exception):
    "Raised when there is an issue authenticating with the Nexus API."


class ResourceFetchFailed(Exception):
    """
    Raised when a resource cannot be fetched from the platform to be read, or
    when expected data wasn't found on an object.
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
    """Raised when a ``get`` call finds no matches."""


class NoUniqueMatch(Exception):
    """Raised when a ``get`` call finds more than one match."""


class JobError(Exception):
    """Raised when a Nexus Job has errored."""


class ResourceCreateFailed(Exception):
    """Raised when a resource couldn't be created on the platform."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to create resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)


class ResourceDeleteFailed(Exception):
    """Raised when a resource couldn't be deleted on the platform."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to delete resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)


class ResourceUpdateFailed(Exception):
    """Raised when a resource cannot be updated on the platform."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        self.message = message
        self.status_code = status_code
        self.err = (
            "Failed to update resource with status code: "
            f"{self.status_code}, message: {self.message}"
        )
        super().__init__(self.err)
