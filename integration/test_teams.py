"""Test basic functionality relating to the team module."""

from datetime import datetime

import pandas as pd

import qnexus as qnx
from qnexus.models.references import TeamRef


def test_team_get(_authenticated_nexus: None, qa_team_name: str) -> None:
    """Test that we can get a specific unique TeamRef."""

    my_team = qnx.teams.get(name=qa_team_name)
    assert isinstance(my_team, TeamRef)


def test_team_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get all teams (currently not a NexusIterator)."""

    my_teams = qnx.teams.get_all()

    assert len(my_teams) > 1
    assert isinstance(my_teams.df(), pd.DataFrame)
    assert isinstance(my_teams[0], TeamRef)


def test_team_create(
    _authenticated_nexus: None,
) -> None:
    """Test that we can create a team."""

    team_name = f"qa_test_team_{datetime.now()}"
    team_description = "A test team (can be deleted)"

    my_new_team = qnx.teams.create(name=team_name, description=team_description)

    assert isinstance(my_new_team, TeamRef)
    assert my_new_team.name == team_name
    assert my_new_team.description == team_description
