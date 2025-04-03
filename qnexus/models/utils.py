"""Utility models for use by the client."""

from typing import Any, NoReturn

from pydantic import ValidatorFunctionWrapHandler
from pydantic.functional_validators import WrapValidator


def allow_none(v: Any, handler: ValidatorFunctionWrapHandler) -> Any:
    """Custom validator to allow None values."""
    if v is None:
        return v
    return handler(v)


AllowNone = WrapValidator(allow_none)


def assert_never(never: NoReturn) -> NoReturn:
    """Used to enforce exhaustiveness in a match statement.

    https://github.com/microsoft/pyright/issues/2569"""
    assert False, f"Unhandled type: f{never}"
