"""Utility models for use by the client."""

from typing import Any

from pydantic import ValidatorFunctionWrapHandler
from pydantic.functional_validators import WrapValidator


def allow_none(v: Any, handler: ValidatorFunctionWrapHandler) -> None:
    """Custom validator to allow None values."""
    if v is None:
        return v
    return handler(v)


AllowNone = WrapValidator(allow_none)
