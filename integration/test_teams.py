"""Test basic functionality relating to the team module."""

from typing import Callable, ContextManager

import pandas as pd

import qnexus as qnx
from qnexus.models.references import Ref, TeamRef


def test_team_get(
    test_case_name: str,
    create_team: Callable[[str], ContextManager[TeamRef]],
    test_ref_serialisation: Callable[[str, Ref], None],
) -> None:
    """Test that we can get a specific unique TeamRef and its
    serialisation round trip."""

    team_name = f"{test_case_name[-86:]}"  # TODO: use full name once bug is fixed

    with create_team(team_name):
        my_team = qnx.teams.get(name=team_name)
        assert isinstance(my_team, TeamRef)

        test_ref_serialisation("team", my_team)


def test_team_get_all(
    test_case_name: str,
    create_team: Callable[[str], ContextManager[TeamRef]],
) -> None:
    """Test that we can get all teams (currently not a NexusIterator)."""

    team_name = f"{test_case_name[-86:]}"  # TODO: use full name once bug is fixed

    with create_team(team_name):
        my_teams = qnx.teams.get_all()

        assert len(my_teams) >= 1
        assert isinstance(my_teams.df(), pd.DataFrame)
        assert isinstance(my_teams[0], TeamRef)


def test_team_create(
    test_case_name: str,
    authenticated_nexus: None,
) -> None:
    """Test that we can create a team."""

    team_name = f"{test_case_name[-86:]}"  # TODO: use full name once bug is fixed
    team_description = "A test team (can be deleted)"

    my_new_team = qnx.teams.create(name=team_name, description=team_description)

    assert isinstance(my_new_team, TeamRef)
    assert my_new_team.name == team_name
    assert my_new_team.description == team_description
