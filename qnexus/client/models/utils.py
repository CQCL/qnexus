from typing import Annotated, Any

from pydantic import ValidatorFunctionWrapHandler
from pydantic.functional_validators import WrapValidator


def allow_none(v: Any, handler: ValidatorFunctionWrapHandler) -> int:
    if v is None:
        return v
    return handler(v)


AllowNone = WrapValidator(allow_none)
