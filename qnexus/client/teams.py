""" """

from qnexus.client import nexus_client
import qnexus.exceptions as qnx_exc
from qnexus.client.pagination_iterator import RefList
from qnexus.references import TeamsRef



def filter() -> list[TeamsRef]:
    """ No fuzzy name matching."""
    res = nexus_client.get(
        "/api/v5/user/teams",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.json(), status_code=res.status_code)
    
    return RefList([TeamsRef(
            id=team["id"],
            name=team["team_name"],
            description=team["description"],
        ) for team in res.json()
    ])



def get(name: str) -> TeamsRef:
    """ No fuzzy name matching."""
    res = nexus_client.get(
        "/api/v5/user/teams",
        params={"name": name}
    )

    if res.status_code == 404:
        raise qnx_exc.ZeroMatches

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.json(), status_code=res.status_code)
    
    teams_list = [TeamsRef(
            id=team["id"],
            name=team["team_name"],
            description=team["description"],
        ) for team in res.json()
    ]

    if len(teams_list) > 1:
        raise qnx_exc.NoUniqueMatch

    return teams_list[0]
