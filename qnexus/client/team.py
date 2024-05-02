"""Client API for teams in Nexus."""

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.references import DataframableList, TeamsRef


def get() -> list[TeamsRef]:
    """No fuzzy name matching."""
    res = nexus_client.get(
        "/api/v5/user/teams",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    return DataframableList(
        [
            TeamsRef(
                id=team["id"],
                name=team["team_name"],
                description=team["description"],
            )
            for team in res.json()
        ]
    )


def get_only(name: str) -> TeamsRef:
    """Attempt to get an exact match on a team by using filters
    that uniquely identify one."""
    res = nexus_client.get("/api/v5/user/teams", params={"name": name})

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    teams_list = [
        TeamsRef(
            id=team["id"],
            name=team["team_name"],
            description=team["description"],
        )
        for team in res.json()
    ]

    if len(teams_list) > 1:
        raise qnx_exc.NoUniqueMatch

    return teams_list[0]


def create() -> TeamsRef:
    """Create a team in Nexus."""
    raise NotImplementedError
