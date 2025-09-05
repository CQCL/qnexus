"""Client API for users in Nexus."""

from uuid import UUID

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.models.references import UserRef


def get_self() -> UserRef:
    """Get the logged in user."""

    res = get_nexus_client().get("/api/users/v1beta2/me")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    user_dict = res.json()

    return UserRef(
        display_name=user_dict["data"]["attributes"]["display_name"],
        id=user_dict["data"]["id"],
    )


def _fetch_by_id(user_id: UUID) -> UserRef:
    """Get a specific user."""

    res = get_nexus_client().get(f"/api/users/v1beta/{user_id}")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    user_dict = res.json()

    return UserRef(
        display_name=user_dict["data"]["attributes"]["display_name"],
        id=user_dict["data"]["id"],
    )
