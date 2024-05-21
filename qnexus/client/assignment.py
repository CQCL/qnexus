"""Client API for role-based-access-control assignments in Nexus."""
from typing import Literal

from pydantic import EmailStr

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.client.models import Role
from qnexus.references import BaseRef, DataframableList, TeamRef

Permission = Literal["ASSIGN", "DELETE", "WRITE", "READ"]
RoleName = Literal["Administrator", "Contributor", "Reader", "Maintainer"]


def get() -> DataframableList[Role]:
    """Get the definitions of possible role-based access control assignments."""
    res = nexus_client.get(
        "/api/roles/v1beta",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    return DataframableList([
        Role(
            id=role["id"],
            name=role["attributes"]["name"],
            description=role["attributes"]["description"],
            permissions=str(role["attributes"]["permissions"]),
        ) for role in res.json()["data"]]
    )



def get_only(name: RoleName) -> Role:
    """Get a unique role-based access control assignment"""
    for item in get():
        if item.name == name:
            return item

    raise qnx_exc.NoUniqueMatch()


def assign_team_role(
    resource_ref: BaseRef, team: TeamRef, role: RoleName | Role
) -> None:
    """Assign a role-based access control assignment to a team."""
    if isinstance(role, str):
        role = get_only(role)

    req_dict = {
        "data": {
            "attributes": {
                "role_id": str(role.id),
                "resource_id": str(resource_ref.id),
                "team_id": str(team.id),
            },
            "relationships": None,
            "type": "team_role_assignment",
        }
    }

    res = nexus_client.post(
        "/api/assignments/v1beta/team",
        json=req_dict,
    )

    if res.status_code != 201:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.json(), status_code=res.status_code
        )


def assign_user_role(
    resource_ref: BaseRef, user_email: EmailStr, role: RoleName | Role
) -> None:
    """Assign a role-based access control assignment to a user."""
    if isinstance(role, str):
        role = get_only(role)

    req_dict = {
        "data": {
            "attributes": {
                "role_id": str(role.id),
                "resource_id": str(resource_ref.id),
                "user": {"user_email": user_email},
            },
            "relationships": None,
            "type": "user_role_assignment",
        }
    }

    res = nexus_client.post(
        "/api/assignments/v1beta/user",
        json=req_dict,
    )

    if res.status_code != 201:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.json(), status_code=res.status_code
        )
