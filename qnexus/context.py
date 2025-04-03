"""Functions for managing context in the client."""

import logging
from contextlib import contextmanager
from contextvars import ContextVar, Token
from functools import wraps
from typing import Any, Callable, Generator, ParamSpec, TypeVar

from qnexus.models.annotations import PropertiesDict
from qnexus.models.references import ProjectRef

logger = logging.getLogger(__name__)

_QNEXUS_PROJECT: ContextVar[ProjectRef | None] = ContextVar(
    "qnexus_project", default=None
)
_QNEXUS_PROPERTIES: ContextVar[PropertiesDict | None] = ContextVar(
    "qnexus_properties", default=None
)


def deactivate_project(token: Token[ProjectRef | None]) -> None:
    """Deactivate a project from the current context."""
    _QNEXUS_PROJECT.reset(token)


def deactivate_properties(token: Token[PropertiesDict | None]) -> None:
    """Deactivate the current properties."""
    _QNEXUS_PROPERTIES.reset(token)


def get_active_project(project_required: bool = False) -> ProjectRef | None:
    """Get a reference to the active project if set.

    >>> get_active_project()

    >>> from qnexus.models.annotations import Annotations
    >>> token = set_active_project_token(
    ... ProjectRef(id="dca33f7f-9619-4cf7-a3fb-56256b117d6e",
    ... annotations=Annotations(name="example")))
    >>> get_active_project()
    ProjectRef(
        id=UUID('dca33f7f-9619-4cf7-a3fb-56256b117d6e'),
        annotations=Annotations(name='example', description=None, properties=OrderedDict())
    )

    >>> deactivate_project(token)

    """
    active_project = _QNEXUS_PROJECT.get(None)
    if active_project is None and project_required:
        raise UnboundLocalError("No Project set.")
    return active_project


def get_active_properties() -> PropertiesDict:
    """Get the keys and values of the currently active properties.

    >>> get_active_properties()
    OrderedDict()

    >>> token = update_active_properties_token(foo=3, bar=True)
    >>> get_active_properties()
    OrderedDict([('foo', 3), ('bar', True)])

    >>> deactivate_properties(token)

    """
    properties = _QNEXUS_PROPERTIES.get()
    if properties is None:
        return PropertiesDict()
    return properties


def set_active_project_token(project: ProjectRef) -> Token[ProjectRef | None]:
    """Globally set a project as active,
    returning a Token to the ProjectRef in the context."""
    return _QNEXUS_PROJECT.set(project)


def set_active_project(project: ProjectRef) -> None:
    """Globally set a project as active."""
    set_active_project_token(project)


def update_active_properties_token(
    **properties: int | float | str | bool,
) -> Token[PropertiesDict | None]:
    """Globally update and merge properties with the existing ones,
    returning a token to the PropertiesDict in the context."""
    current_properties = _QNEXUS_PROPERTIES.get()
    if current_properties is None:
        current_properties = PropertiesDict({})
    else:
        current_properties = current_properties.copy()

    current_properties.update(properties)

    return _QNEXUS_PROPERTIES.set(current_properties)


def update_active_properties(
    **properties: int | float | str | bool,
) -> None:
    """Globally update and merge properties with the existing ones."""
    update_active_properties_token(**properties)


@contextmanager
def using_project(project: ProjectRef) -> Generator[None, None, None]:
    """Attach a ProjectRef to the current context.

    All operations in the context will make use of the project.

    >>> from qnexus.models.annotations import Annotations
    >>> project = ProjectRef(
    ... id="cd325b9c-d4a2-4b6e-ae58-8fad89749fac",
    ... annotations=Annotations(name="example"))
    >>> with using_project(project):
    ...     get_active_project()
    ProjectRef(
        id=UUID('cd325b9c-d4a2-4b6e-ae58-8fad89749fac'),
        annotations=Annotations(name='example', description=None, properties=OrderedDict())
    )

    >>> get_active_project()
    """
    token = set_active_project_token(project)
    try:
        yield
    finally:
        return _QNEXUS_PROJECT.reset(token)


@contextmanager
def using_properties(
    **properties: int | float | str | bool,
) -> Generator[None, None, None]:
    """Attach properties to the current context."""
    token = update_active_properties_token(**properties)
    try:
        yield
    finally:
        _QNEXUS_PROPERTIES.reset(token)


P = ParamSpec("P")
T = TypeVar("T")


def merge_project_from_context(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to merge a project from the context.
    ProjectRef in kwargs takes precedence (will be selected)."""

    @wraps(func)
    def get_project_from_context(*args: Any, **kwargs: Any) -> T:
        kwargs["project"] = kwargs.get("project", None)
        if kwargs["project"] is None:
            kwargs["project"] = get_active_project()
        return func(*args, **kwargs)

    return get_project_from_context


def merge_properties_from_context(func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to take the union of properties from the context with
    any provided in kwargs. Properties in kwargs take precendence."""

    @wraps(func)
    def _merge_properties_from_context(*args: Any, **kwargs: Any) -> T:
        if kwargs.get("properties") is None:
            kwargs["properties"] = PropertiesDict()
        kwargs["properties"] = get_active_properties() | kwargs["properties"]
        return func(*args, **kwargs)

    return _merge_properties_from_context
