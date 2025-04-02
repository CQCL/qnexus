"""Client API for role-based-access-control roles and assignments in Nexus."""

from typing import Literal

from pydantic import EmailStr

import qnexus.client.teams as team_client
import qnexus.client.users as user_client
import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.models import Role, RoleInfo
from qnexus.models.references import BaseRef, DataframableList, TeamRef

Permission = Literal["ASSIGN", "DELETE", "WRITE", "READ"]
RoleName = Literal["Administrator", "Contributor", "Reader", "Maintainer"]


def get_all() -> DataframableList[Role]:
    """Get the definitions of possible role-based access control assignments."""
    res = get_nexus_client().get(
        "/api/roles/v1beta",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    return DataframableList(
        [
            Role(
                id=role["id"],
                name=role["attributes"]["name"],
                description=role["attributes"]["description"],
                permissions=str(role["attributes"]["permissions"]),
            )
            for role in res.json()["data"]
        ]
    )


def get(name: RoleName) -> Role:
    """
    Get a single ``Role`` by name.
    """
    for item in get_all():
        if item.name == name:
            return item

    raise qnx_exc.NoUniqueMatch()


def assignments(resource_ref: BaseRef) -> DataframableList[RoleInfo]:
    """Check the assignments on a particular resource."""

    res = get_nexus_client().get(
        f"/api/resources/v1beta/{resource_ref.id}/assignments",
    )

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    roles_dict = {str(role.id): role for role in get_all()}

    res_assignments = res.json()["data"]["attributes"]

    role_infos: DataframableList[RoleInfo] = DataframableList([])

    for user_role_assignment in res_assignments["user_role_assignments"]:
        role_infos.append(
            RoleInfo(
                assignment_type="user",
                assignee=user_client._fetch_by_id(
                    user_id=user_role_assignment["user_id"]
                ),
                role=roles_dict[user_role_assignment["role_id"]],
            )
        )
    for team_role_assignment in res_assignments["team_role_assignments"]:
        role_infos.append(
            RoleInfo(
                assignment_type="team",
                assignee=team_client._fetch_by_id(
                    team_id=team_role_assignment["team_id"]
                ),
                role=roles_dict[team_role_assignment["role_id"]],
            )
        )
    for public_role_assignment in res_assignments["public_role_assignments"]:
        role_infos.append(
            RoleInfo(
                assignment_type="public",
                assignee=None,
                role=roles_dict[public_role_assignment["role_id"]],
            )
        )
    return role_infos


def assign_team(resource_ref: BaseRef, team: TeamRef, role: RoleName | Role) -> None:
    """Assign a role-based access control assignment to a team."""
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

    res = get_nexus_client().post(
        "/api/assignments/v1beta/team",
        json=req_dict,
    )

    if res.status_code != 201:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.text, status_code=res.status_code
        )


def assign_user(
    resource_ref: BaseRef, user_email: EmailStr, role: RoleName | Role
) -> None:
    """Assign a role-based access control assignment to a user."""
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

    res = get_nexus_client().post(
        "/api/assignments/v1beta/user",
        json=req_dict,
    )

    if res.status_code != 201:
        raise qnx_exc.ResourceUpdateFailed(
            message=res.text, status_code=res.status_code
        )
