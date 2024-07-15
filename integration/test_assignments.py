"""Test basic functionality relating to the assignment module."""

from datetime import datetime

import pandas as pd
from constants import NEXUS_QA_USER_EMAIL

import qnexus as qnx
from qnexus.client.models import Role
from qnexus.references import TeamRef, UserRef


def test_assignment_getonly(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a specific Role."""

    role = qnx.role.get_only(name="Administrator")
    assert isinstance(role, Role)


def test_assignment_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    all_roles = qnx.role.get()

    assert len(all_roles) == 4
    assert isinstance(all_roles.df(), pd.DataFrame)
    assert isinstance(all_roles[0], Role)


def test_team_assignment(
    _authenticated_nexus: None,
    qa_team_name: str,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.project.create(name=f"QA_test_project_{datetime.now()}_0")

    team = qnx.team.get_only(name=qa_team_name)

    qnx.role.assign_team_role(
        resource_ref=new_project_ref, team=team, role="Administrator"
    )

    assignments = qnx.role.assignments(resource_ref=new_project_ref)

    assert len(assignments) == 2

    team_assignment = next(
        assign for assign in assignments if assign.assignment_type == "team"
    )
    assert team_assignment.assignment_type == "team"
    assert isinstance(team_assignment.assignee, TeamRef)
    assert team_assignment.assignee.id == team.id

    # TODO delete project once available


def test_user_assignment(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.project.create(name=f"QA_test_project_{datetime.now()}_1")

    qnx.role.assign_user_role(
        resource_ref=new_project_ref,
        user_email=NEXUS_QA_USER_EMAIL,
        role="Contributor",
    )

    assignments = qnx.role.assignments(resource_ref=new_project_ref)

    assert len(assignments) == 2

    contrib_assignment = next(
        assign for assign in assignments if assign.role.name == "Contributor"
    )
    assert contrib_assignment.assignment_type == "user"
    assert isinstance(contrib_assignment.assignee, UserRef)

    admin_assignment = next(
        assign for assign in assignments if assign.role.name == "Administrator"
    )
    assert admin_assignment.assignment_type == "user"
    assert isinstance(admin_assignment.assignee, UserRef)

    # TODO delete project once available
