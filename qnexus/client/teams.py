"""Client API for teams in Nexus."""

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.models.references import DataframableList, TeamRef


def get_all() -> DataframableList[TeamRef]:
    """No fuzzy name matching."""
    res = get_nexus_client().get(
        "/api/teams/v1beta2",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    return DataframableList(
        [
            TeamRef(
                id=team["id"],
                name=team["attributes"]["name"],
                description=team["attributes"]["description"],
            )
            for team in res.json()["data"]
        ]
    )


def get(name: str) -> TeamRef:
    """
    Get a single team using filters. Throws an exception if the filters do not
    match exactly one object.
    """
    res = get_nexus_client().get(
        "/api/teams/v1beta2", params={"filter[team][name]": name}
    )

    if res.status_code == 404 or res.json()["data"] == []:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    teams_list = [
        TeamRef(
            id=team["id"],
            name=team["attributes"]["name"],
            description=team["attributes"]["description"],
        )
        for team in res.json()["data"]
    ]

    if len(teams_list) > 1:
        print(teams_list)
        raise qnx_exc.NoUniqueMatch

    return teams_list[0]


def _fetch_by_id(team_id: str) -> TeamRef:
    """
    Get a single team by id.
    """
    res = get_nexus_client().get(f"/api/teams/v1beta2/{team_id}")

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    team_dict = res.json()["data"]

    return TeamRef(
        id=team_dict["id"],
        name=team_dict["attributes"]["name"],
        description=team_dict["attributes"]["description"],
    )


def create(name: str, description: str | None = None) -> TeamRef:
    """Create a team in Nexus."""

    resp = get_nexus_client().post(
        "/api/teams/v1beta2",
        json={
            "data": {
                "attributes": {
                    "name": name,
                    "description": description,
                    "display_name": name,
                },
                "relationships": {},
                "type": "team",
            },
        },
    )

    if resp.status_code != 201:
        raise qnx_exc.ResourceCreateFailed(
            message=resp.text, status_code=resp.status_code
        )

    team_dict = resp.json()["data"]
    return TeamRef(
        id=team_dict["id"],
        name=team_dict["attributes"]["name"],
        description=team_dict["attributes"]["description"],
    )
