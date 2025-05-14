"""Test basic functionality relating to the role module."""

from datetime import datetime

import pandas as pd

import qnexus as qnx
from qnexus.config import CONFIG
from qnexus.models import Role
from qnexus.models.references import TeamRef, UserRef


def test_role_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a specific Role."""

    role = qnx.roles.get(name="Administrator")
    assert isinstance(role, Role)


def test_role_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    all_roles = qnx.roles.get_all()

    assert len(all_roles) == 4
    assert isinstance(all_roles.df(), pd.DataFrame)
    assert isinstance(all_roles[0], Role)


def test_team_assignment(
    _authenticated_nexus: None,
    qa_team_name: str,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.projects.create(name=f"QA_test_project_{datetime.now()}_0")

    team = qnx.teams.get(name=qa_team_name)

    qnx.roles.assign_team(resource_ref=new_project_ref, team=team, role="Administrator")

    assignments = qnx.roles.assignments(resource_ref=new_project_ref)

    assert len(assignments) == 2

    team_assignment = next(
        assign for assign in assignments if assign.assignment_type == "team"
    )
    assert team_assignment.assignment_type == "team"
    assert isinstance(team_assignment.assignee, TeamRef)
    assert team_assignment.assignee.id == team.id

    qnx.projects.update(new_project_ref, archive=True)
    qnx.projects.delete(new_project_ref)


def test_user_assignment(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all assignment role definitions."""

    new_project_ref = qnx.projects.create(name=f"QA_test_project_{datetime.now()}_1")

    qnx.roles.assign_user(
        resource_ref=new_project_ref,
        user_email=CONFIG.qa_user_email,
        role="Contributor",
    )

    assignments = qnx.roles.assignments(resource_ref=new_project_ref)

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

    qnx.projects.update(new_project_ref, archive=True)
    qnx.projects.delete(new_project_ref)
