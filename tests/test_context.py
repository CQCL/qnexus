"""Test the context management system."""

from collections import OrderedDict
from datetime import datetime
from uuid import uuid4

import pytest

from qnexus.context import (
    deactivate_project,
    get_active_project,
    get_active_properties,
    merge_project_from_context,
    merge_properties_from_context,
    set_active_project_token,
    using_project,
    using_properties,
)
from qnexus.models.annotations import Annotations, PropertiesDict
from qnexus.models.references import ProjectRef


def test_attach_project() -> None:
    """Test that we can set a Project in the global context."""
    project_id = uuid4()
    project = ProjectRef(
        id=project_id,
        annotations=Annotations(name=""),
        contents_modified=datetime.now(),
        archived=False,
    )

    token = set_active_project_token(project=project)

    ctx_project = get_active_project()

    assert project == ctx_project

    deactivate_project(token)


def test_attach_project_context_manager() -> None:
    """Test that we can set a Project via a context manager."""

    project_id = uuid4()
    project = ProjectRef(
        id=project_id,
        annotations=Annotations(name=""),
        contents_modified=datetime.now(),
        archived=False,
    )
    with using_project(project=project):
        ctx_project = get_active_project()

        assert project == ctx_project

    ctx_project = get_active_project()

    assert ctx_project is None


def test_attach_properties() -> None:
    """Test that we can set properties in the global context."""
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


def test_merge_project_from_context() -> None:
    """Test the decorator for merging a projectref from context or function arguments."""

    project = ProjectRef(
        id=uuid4(),
        annotations=Annotations(
            name="test_project",
        ),
        contents_modified=datetime.now(),
        archived=False,
    )

    @merge_project_from_context
    def func_wants_project(project: ProjectRef | None = None) -> ProjectRef:
        """Dummy function for testing the merge_project decorator"""
        assert project is not None
        assert isinstance(project, ProjectRef)
        return project

    with pytest.raises(AssertionError):
        func_wants_project()

    returned_project = func_wants_project(project=project)
    assert returned_project == project

    with using_project(project=project):
        returned_project = func_wants_project()
        assert returned_project == project

    other_project = ProjectRef(
        id=uuid4(),
        annotations=Annotations(
            name="test_project_2",
        ),
        contents_modified=datetime.now(),
        archived=False,
    )

    with using_project(project=project):
        # kwarg takes precedence
        returned_project = func_wants_project(project=other_project)
        assert returned_project == other_project


def test_merge_properties_from_context() -> None:
    """Test the decorator for merging properties from context or function arguments."""

    @merge_properties_from_context
    def func_wants_properties(
        properties: PropertiesDict | None = None,
    ) -> PropertiesDict:
        """Dummy function for testing the merge_properties decorator"""
        # Property decorator provides empty properties dict by default
        assert isinstance(properties, OrderedDict)
        return properties

    assert func_wants_properties() == PropertiesDict({})

    first_props = PropertiesDict({"1": 2, "shared_key": "world"})

    returned_props = func_wants_properties(properties=first_props)
    assert returned_props == first_props

    with using_properties(**first_props):
        returned_props = func_wants_properties()
        assert returned_props == first_props

    second_props = PropertiesDict({"bingo": 2, "shared_key": 2.01})

    with using_properties(**first_props):
        # kwarg props take precedence, but otherwise union is taken
        returned_props = func_wants_properties(properties=second_props)

        assert returned_props["1"] == first_props["1"]
        assert returned_props["bingo"] == second_props["bingo"]
        assert returned_props["shared_key"] == second_props["shared_key"]
        assert len(returned_props.keys()) == 3


def test_merge_only_properties_from_context() -> None:
    """Test the decorator for merging properties from context when no properties are
    passed as an argument."""

    @merge_properties_from_context
    def func_wants_properties(
        properties: PropertiesDict | None = None,
    ) -> PropertiesDict:
        """Dummy function for testing the merge_properties decorator"""
        # Property decorator provides empty properties dict by default
        assert isinstance(properties, OrderedDict)
        return properties

    assert func_wants_properties() == PropertiesDict({})

    test_props = PropertiesDict({"1": 2, "shared_key": "world"})

    with using_properties(**test_props):
        returned_props = func_wants_properties(properties=None)
        assert returned_props == test_props
