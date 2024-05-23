"""Test basic functionality relating to the assignment module."""

from datetime import datetime

import pandas as pd
import pytest
from constants import NEXUS_QA_USER_EMAIL

import qnexus as qnx
from qnexus.client.models import Role


def test_assignment_getonly(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a specific Role."""

    role = qnx.assignment.get_only(name="Administrator")
    assert isinstance(role, Role)


def test_assignment_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    all_roles = qnx.assignment.get()

    assert len(all_roles) == 4
    assert isinstance(all_roles.df(), pd.DataFrame)
    assert isinstance(all_roles[0], Role)


@pytest.mark.create
def test_team_assignment(
    _authenticated_nexus: None,
    qa_team_name: str,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.project.create(name=f"QA_test_project_{datetime.now()}_0")

    team = qnx.team.get_only(name=qa_team_name)

    qnx.assignment.assign_team_role(
        resource_ref=new_project_ref, team=team, role="Administrator"
    )

    # TODO verify assignment, delete project


@pytest.mark.create
def test_user_assignment(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.project.create(name=f"QA_test_project_{datetime.now()}_1")

    qnx.assignment.assign_user_role(
        resource_ref=new_project_ref,
        user_email=NEXUS_QA_USER_EMAIL,
        role="Contributor",
    )

    # TODO verify assignment, delete project
