"""Test basic functionality relating to the project module."""

from datetime import datetime

import pandas as pd
import pytest

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.references import ProjectRef


def test_project_get(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get a specific unique project
    by name or id, or get an appropriate exception."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    assert isinstance(my_proj, ProjectRef)

    my_proj_2 = qnx.projects.get(id=my_proj.id)
    assert my_proj == my_proj_2

    with pytest.raises(qnx_exc.NoUniqueMatch):
        qnx.projects.get()

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.projects.get(name_like=f"{datetime.now()}_{datetime.now()}")


def test_project_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get an iterator over all projects."""

    my_proj_db_matches = qnx.projects.get_all()

    assert isinstance(my_proj_db_matches.count(), int)
    assert isinstance(my_proj_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_proj_db_matches), ProjectRef)


def test_project_create(
    _authenticated_nexus: None,
) -> None:
    """Test that we can create a project and add a property definition."""

    project_name = f"QA_test_project_create_{datetime.now()}"

    my_new_project = qnx.projects.create(name=project_name)

    assert isinstance(my_new_project, ProjectRef)

    test_property_name = "QA_test_prop"

    qnx.projects.add_property(
        name="QA_test_prop",
        property_type="bool",
        project=my_new_project,
        description="A test property for my QA test project",
    )

    test_props = qnx.projects.get_properties(my_new_project)

    assert len(test_props) == 1
    assert test_props[0].annotations.name == test_property_name

    with pytest.raises(qnx_exc.ResourceDeleteFailed):
        qnx.projects.delete(my_new_project)

    qnx.projects.update(my_new_project, archive=True)

    qnx.projects.delete(my_new_project)

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.projects.get(name_like=project_name)


def test_project_get_or_create(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get or create a project."""

    project_name = f"QA_test_project_get_or_create_{datetime.now()}"

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.projects.get(name_like=project_name)

    my_new_project = qnx.projects.get_or_create(name=project_name)

    assert isinstance(my_new_project, ProjectRef)

    my_new_project_again = qnx.projects.get_or_create(name=project_name)

    assert my_new_project == my_new_project_again

    qnx.projects.update(my_new_project, archive=True)
    qnx.projects.delete(my_new_project)


def test_project_summarize(
    _authenticated_nexus: None,
    qa_project_name: str,
) -> None:
    """Test that we can get summary information on the state of a project."""

    my_proj = qnx.projects.get(name_like=qa_project_name)
    assert isinstance(my_proj, ProjectRef)

    project_summary = qnx.projects.summarize(my_proj)

    assert isinstance(project_summary, pd.DataFrame)

    assert (project_summary["total_jobs"] > 0).all()
