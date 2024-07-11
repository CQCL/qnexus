"""Test basic functionality relating to the project module."""

from datetime import datetime

import pandas as pd
import pytest

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.references import ProjectRef


def test_project_getonly(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get a specific unique project,
    or get an appropriate exception."""

    my_proj = qnx.project.get_only(name_like=qa_project_name)
    assert isinstance(my_proj, ProjectRef)

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.project.get_only()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.project.get_only(name_like=f"{datetime.now()}_{datetime.now()}")


def test_project_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get an iterator over all projects."""

    my_proj_db_matches = qnx.project.get()

    assert isinstance(my_proj_db_matches.count(), int)
    assert isinstance(my_proj_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_proj_db_matches), ProjectRef)


def test_project_create(
    _authenticated_nexus: None,
) -> None:
    """Test that we can create a project and add a property definition."""

    project_name = f"QA_test_project_create_{datetime.now()}"

    my_new_project = qnx.project.create(name=project_name)

    assert isinstance(my_new_project, ProjectRef)

    test_property_name = "QA_test_prop"

    qnx.project.add_property(
        name="QA_test_prop",
        property_type="bool",
        project=my_new_project,
        description="A test property for my QA test project",
    )

    test_props = qnx.project.get_properties(my_new_project)

    assert len(test_props) == 1
    assert test_props[0].annotations.name == test_property_name
