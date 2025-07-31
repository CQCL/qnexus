"""Test basic functionality relating to the project module."""

from datetime import datetime
from typing import Callable, ContextManager

import pandas as pd
import pytest
from pytket.circuit import Circuit

import qnexus as qnx
import qnexus.exceptions as qnx_exc
from qnexus.models.references import CompileJobRef, ProjectRef, Ref


def test_project_get(
    test_case_name: str,
    create_project: Callable[[str], ContextManager[ProjectRef]],
    test_ref_serialisation: Callable[[str, Ref], None],
) -> None:
    """Test that we can get a specific unique project
    by name or id, or get an appropriate exception."""

    with create_project(f"project for {test_case_name}") as proj_ref:
        assert isinstance(proj_ref, ProjectRef)

        my_proj_2 = qnx.projects.get(id=proj_ref.id)
        assert proj_ref == my_proj_2

        with pytest.raises(qnx_exc.NoUniqueMatch):
            qnx.projects.get()

        with pytest.raises(qnx_exc.ZeroMatches):
            qnx.projects.get(name_like=f"{datetime.now()}_{datetime.now()}")

        test_ref_serialisation("project", my_proj_2)


def test_project_get_all(authenticated_nexus: None) -> None:
    """Test that we can get an iterator over all projects."""

    my_proj_db_matches = qnx.projects.get_all()

    assert isinstance(my_proj_db_matches.count(), int)
    assert isinstance(my_proj_db_matches.summarize(), pd.DataFrame)

    assert isinstance(next(my_proj_db_matches), ProjectRef)


def test_project_create(
    test_case_name: str,
    authenticated_nexus: None,
) -> None:
    """Test that we can create a project and add a property definition."""

    project_name = f"project for {test_case_name}"

    my_new_project = qnx.projects.create(name=project_name)

    assert isinstance(my_new_project, ProjectRef)

    test_property_name = f"property for {test_case_name}"

    qnx.projects.add_property(
        name=test_property_name,
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
    test_case_name: str,
    authenticated_nexus: None,
) -> None:
    """Test that we can get or create a project."""

    project_name = f"project for {test_case_name}"

    with pytest.raises(qnx_exc.ZeroMatches):
        qnx.projects.get(name_like=project_name)

    my_new_project = qnx.projects.get_or_create(name=project_name)

    assert isinstance(my_new_project, ProjectRef)

    my_new_project_again = qnx.projects.get_or_create(name=project_name)

    assert my_new_project == my_new_project_again

    qnx.projects.update(my_new_project, archive=True)
    qnx.projects.delete(my_new_project)


def test_project_summarize(
    test_case_name: str,
    create_compile_job_in_project: Callable[..., ContextManager[CompileJobRef]],
) -> None:
    """Test that we can get summary information on the state of a project."""
    project_name = f"project for {test_case_name}"
    circuit_name = f"circuit for {test_case_name}"
    compile_job_name = f"compile job for {test_case_name}"

    with create_compile_job_in_project(
        project_name=project_name,
        job_name=compile_job_name,
        circuit=Circuit(2, 2).H(0).CX(0, 1).measure_all(),
        circuit_name=circuit_name,
    ):
        my_proj = qnx.projects.get(name_like=project_name)
        assert isinstance(my_proj, ProjectRef)

        project_summary = qnx.projects.summarize(my_proj)

        assert isinstance(project_summary, pd.DataFrame)

        assert (project_summary["total_jobs"] > 0).all()
