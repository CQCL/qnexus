from contextlib import contextmanager
from contextvars import ContextVar, Token
import logging
from qnexus.annotations import PropertiesDict

from qnexus.references import ProjectRef

logger = logging.getLogger(__name__)

_QNEXUS_PROJECT: ContextVar[ProjectRef | None] = ContextVar(
    "qnexus_project", default=None
)
_QNEXUS_PROPERTIES: ContextVar[PropertiesDict | None] = ContextVar(
    "qnexus_properties", default=None
)


def deactivate_project(token: Token[ProjectRef | None]) -> ProjectRef | None:
    """Deactivate a project from the current context and return the reference."""
    return _QNEXUS_PROJECT.reset(token)


def deactivate_properties(token: Token[PropertiesDict | None]) -> ProjectRef | None:
    """Deactivate the current properties and return their keys and values."""
    return _QNEXUS_PROPERTIES.reset(token)


def get_active_project() -> ProjectRef | None:
    """Get a reference to the active project if set.

    >>> get_active_project()

    >>> from qnexus.annotations import Annotations
    >>> token = set_active_project(ProjectRef(id="dca33f7f-9619-4cf7-a3fb-56256b117d6e", annotations=Annotations(name="example")))
    >>> get_active_project()
    ProjectRef(id=UUID('dca33f7f-9619-4cf7-a3fb-56256b117d6e'), annotations=Annotations(name='example', description=None, properties={}))

    >>> deactivate_project(token)

    """
    return _QNEXUS_PROJECT.get(None)


def get_active_properties() -> PropertiesDict:
    """Get the keys and values of the currently active properties.

    >>> get_active_properties()
    {}

    >>> token = update_active_properties(foo=3, bar=True)
    >>> get_active_properties()
    {'foo': 3, 'bar': True}

    >>> deactivate_properties(token)

    """
    properties = _QNEXUS_PROPERTIES.get()
    if properties is None:
        return PropertiesDict()
    else:
        return properties


def set_active_project(project: ProjectRef) -> Token[ProjectRef | None]:
    """Globally set a project as active."""
    return _QNEXUS_PROJECT.set(project)


def update_active_properties(
    **properties: int | float | str | bool,
) -> Token[PropertiesDict | None]:
    """Globally update and merge properties with the existing ones."""
    current_properties = _QNEXUS_PROPERTIES.get()
    if current_properties is None:
        current_properties = dict()
    else:
        current_properties = current_properties.copy()

    current_properties.update(properties)

    return _QNEXUS_PROPERTIES.set(current_properties)


@contextmanager
def using_project(project: ProjectRef):
    """Attach a ProjectRef to the current context.

    All operations in the context will make use of the project.

    >>> from qnexus.annotations import Annotations
    >>> project = ProjectRef(id="cd325b9c-d4a2-4b6e-ae58-8fad89749fac", annotations=Annotations(name="example"))
    >>> with using_project(project):
    ...     get_active_project()
    ProjectRef(id=UUID('cd325b9c-d4a2-4b6e-ae58-8fad89749fac'), annotations=Annotations(name='example', description=None, properties={}))

    >>> get_active_project()
    """
    token = set_active_project(project)
    try:
        yield
    finally:
        _QNEXUS_PROJECT.reset(token)


@contextmanager
def using_properties(**properties: int | float | str | bool):
    token = update_active_properties(**properties)
    try:
        yield
    finally:
        _QNEXUS_PROPERTIES.reset(token)