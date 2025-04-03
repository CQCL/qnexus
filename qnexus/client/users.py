"""Client API for users in Nexus."""

from uuid import UUID

import qnexus.exceptions as qnx_exc
from qnexus.client import get_nexus_client
from qnexus.models.references import UserRef


def get_self() -> UserRef:
    """Get the logged in user."""

    res = get_nexus_client().get("/api/v6/user/me")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    user_dict = res.json()

    return UserRef(
        display_name=user_dict["display_name"],
        id=user_dict["id"],
    )


def _fetch_by_id(user_id: UUID) -> UserRef:
    """Get a specific user."""

    res = get_nexus_client().get(f"/api/v6/user/{user_id}")

    if res.status_code != 200:
        raise qnx_exc.ResourceFetchFailed(message=res.text, status_code=res.status_code)

    user_dict = res.json()

    return UserRef(
        display_name=user_dict["display_name"],
        id=user_dict["id"],
    )
