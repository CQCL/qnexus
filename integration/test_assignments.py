"""Test basic functionality relating to the role module."""

from typing import Callable, ContextManager

import pandas as pd

import qnexus as qnx
from qnexus.config import CONFIG
from qnexus.models import Role
from qnexus.models.references import ProjectRef, TeamRef, UserRef


def test_role_get(authenticated_nexus: None) -> None:
    """Test that we can get a specific Role."""

    role = qnx.roles.get(name="Administrator")
    assert isinstance(role, Role)


def test_role_get_all(authenticated_nexus: None) -> None:
    """Test that we can get all assignment role definitions."""

    all_roles = qnx.roles.get_all()

    assert len(all_roles) == 4
    assert isinstance(all_roles.df(), pd.DataFrame)
    assert all([isinstance(role, Role) for role in list(all_roles)])


def test_team_assignment(
    test_case_name: str,
    create_project: Callable[[str], ContextManager[ProjectRef]],
    create_team: Callable[[str], ContextManager[TeamRef]],
) -> None:
    """Test that we can assign a team to a project."""

    # Set up
    team_name = f"{test_case_name[-86:]}"  # TODO: use full name once bug is fixed
    project_name = f"project for {test_case_name}"

    with create_team(team_name) as team_ref:
        with create_project(project_name) as proj_ref:
            qnx.roles.assign_team(
                resource_ref=proj_ref, team=team_ref, role="Administrator"
            )
            assignments = qnx.roles.assignments(resource_ref=proj_ref)
            assert len(assignments) == 2

            team_assignment = next(
                assign for assign in assignments if assign.assignment_type == "team"
            )
            assert team_assignment.assignment_type == "team"
            assert isinstance(team_assignment.assignee, TeamRef)
            assert team_assignment.assignee.id == team_ref.id


def test_user_assignment(
    test_case_name: str, create_project: Callable[[str], ContextManager[ProjectRef]]
) -> None:
    """Test that we can assign a role to a user."""
    with create_project(f"project for {test_case_name}") as new_project_ref:
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
