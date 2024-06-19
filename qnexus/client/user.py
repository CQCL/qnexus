"""Module for actions related to users in Nexus."""
from uuid import UUID

import qnexus.exceptions as qnx_exc
from qnexus.client import nexus_client
from qnexus.references import UserRef


def get_only(user_id: UUID) -> UserRef:
    """Get a specific user."""

    res = nexus_client.get(f"/api/v6/user/{user_id}")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    user_dict = res.json()

    return UserRef(
        email=user_dict["user_name"],
        display_name=user_dict["display_name"],
        id=user_dict["id"],
    )


def get_self() -> UserRef:
    """Get the logged in user."""

    res = nexus_client.get("/api/v6/user/me")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(
            message=res.json(), status_code=res.status_code
        )

    user_dict = res.json()

    return UserRef(
        email=user_dict["user_name"],
        display_name=user_dict["display_name"],
        id=user_dict["id"],
    )
