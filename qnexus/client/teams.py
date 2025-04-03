"""Client API for teams in Nexus."""

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.models.references import DataframableList, TeamRef


def get_all() -> DataframableList[TeamRef]:
    """No fuzzy name matching."""
    res = get_nexus_client().get(
        "/api/v5/user/teams",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    return DataframableList(
        [
            TeamRef(
                id=team["id"],
                name=team["team_name"],
                description=team["description"],
            )
            for team in res.json()
        ]
    )


def get(name: str) -> TeamRef:
    """
    Get a single team using filters. Throws an exception if the filters do not
    match exactly one object.
    """
    res = get_nexus_client().get("/api/v5/user/teams", params={"name": name})

    if res.status_code == 404 or res.json() == []:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    teams_list = [
        TeamRef(
            id=team["id"],
            name=team["team_name"],
            description=team["description"],
        )
        for team in res.json()
    ]

    if len(teams_list) > 1:
        raise qnx_exc.NoUniqueMatch

    return teams_list[0]


def _fetch_by_id(team_id: str) -> TeamRef:
    """
    Get a single team by id.
    """
    res = get_nexus_client().get(f"/api/v5/user/teams/{team_id}")

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    team_dict = res.json()

    return TeamRef(
        id=team_dict["id"],
        name=team_dict["team_name"],
        description=team_dict["description"],
    )


def create(name: str, description: str | None = None) -> TeamRef:
    """Create a team in Nexus."""

    resp = get_nexus_client().post(
        "api/v5/user/teams/new",
        json={
            "team_name": name,
            "description": description,
        },
    )

    if resp.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=resp.text, status_code=resp.status_code
        )

    team_dict = resp.json()
    return TeamRef(
        id=team_dict["id"],
        name=team_dict["team_name"],
        description=team_dict["description"],
    )
