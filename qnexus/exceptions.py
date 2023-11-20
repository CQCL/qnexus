"""Custom exceptions thrown in qnexus usage."""

from typing import Optional


class NotAuthenticatedException(Exception):
    "Raised when the user's tokens have expired."
    pass


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


class ResourceCreateFailed(Exception):
    """ResourceCreateFailed is an exception that occurs when a resource
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
