""" """
from typing import Literal

from pydantic import EmailStr

from qnexus.client import nexus_client
from qnexus.client.pagination_iterator import RefList
from qnexus.exceptions import ResourceFetchFailed, ResourceUpdateFailed
from qnexus.references import BaseRef, NexusRole, TeamsRef

Permission = Literal["ASSIGN", "DELETE", "WRITE", "READ"]
RoleName = Literal["Administrator", "Contributor", "Reader", "Maintainer"]


def filter() -> RefList:
    """ """
    res = nexus_client.get(
        "/api/roles/v1beta",
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    # TODO is there a way of custom deserialisation via pydantic?
    roles = RefList([])

    for role in res.json()["data"]:
        roles.append(
            NexusRole(
                id=role["id"],
                name=role["attributes"]["name"],
                description=role["attributes"]["description"],
                permissions=str(role["attributes"]["permissions"]),
            )
        )

    return roles


def get(name: RoleName) -> NexusRole:
    """ """
    for item in filter():
        if item.name == name:
            return item

    raise Exception()


def assign_team_role(
    resource_ref: BaseRef, team: TeamsRef, role: RoleName | NexusRole
) -> None:
    """ """
    if isinstance(role, str):
        role = get(role)

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
        raise ResourceUpdateFailed(message=res.json(), status_code=res.status_code)


def assign_user_role(
    resource_ref: BaseRef, user_email: EmailStr, role: RoleName | NexusRole
) -> None:
    """ """
    if isinstance(role, str):
        role = get(role)

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
        raise ResourceUpdateFailed(message=res.json(), status_code=res.status_code)
