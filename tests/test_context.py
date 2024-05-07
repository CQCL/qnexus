from uuid import uuid4

from qnexus.annotations import Annotations
from qnexus.context import (
    deactivate_project,
    get_active_project,
    get_active_properties,
    set_active_project,
    using_project,
    using_properties,
)
from qnexus.references import ProjectRef


def test_attach_project() -> None:
    """"""
    project_id = uuid4()
    project_ref = ProjectRef(id=project_id, annotations=Annotations(name=""))

    token = set_active_project(project=project_ref)

    ctx_project = get_active_project()

    assert project_ref == ctx_project

    deactivate_project(token)


def test_attach_project_context_manager() -> None:
    """"""

    project_id = uuid4()
    project_ref = ProjectRef(id=project_id, annotations=Annotations(name=""))
    with using_project(project=project_ref):
        ctx_project = get_active_project()

        assert project_ref == ctx_project

    ctx_project = get_active_project()

    assert ctx_project is None


def test_attach_properties() -> None:
    base_properties = {"foo": 3}
    with using_properties(**base_properties):
        more_properties = {"bar": 5}
        with using_properties(**more_properties):
            ctx_properties = get_active_properties()

            combined_properties = {}
            combined_properties.update(base_properties)
            combined_properties.update(more_properties)

            assert combined_properties == ctx_properties

        ctx_properties = get_active_properties()
        assert base_properties == ctx_properties

    ctx_properties = get_active_properties()

    assert ctx_properties == {}


def test_threading() -> None:
    pass
