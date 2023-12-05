"""Test the token-based auth logic for the httpx Client."""

import httpx
import pytest
import respx

from qnexus.client.client import nexus_client
from qnexus.client import projects
import qnexus.consts
from qnexus.client.utils import write_token, read_token
from qnexus.exceptions import NotAuthenticatedException


@respx.mock
def test_token_refresh() -> None:
    """Test the auth refresh logic, using in-memory token storage."""

    qnexus.consts.STORE_TOKENS = False

    write_token("refresh_token", "dummy_oat")
    write_token("access_token", "dummy_id")
    refreshed_access_token = "new_dummy_id"

    # Mock the list projects endpoint to force a refresh
    list_project_route = respx.get(f"{nexus_client.base_url}/api/projects/v1beta").mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json={"included": {}, "data": []}),
        ]
    )

    # Mock the refresh endpoint
    refresh_token_route = respx.post(
        f"{nexus_client.base_url}/auth/tokens/refresh"
    ).mock(
        return_value=httpx.Response(
            200,
            headers={
                "set-cookie": f"myqos_id={refreshed_access_token}; HttpOnly; Path=/; SameSite=Lax; Secure"
            },
        )
    )

    projects.projects()

    assert list_project_route.called
    assert refresh_token_route.called

    # Confirm that the access token was updated
    assert read_token("access_token") == refreshed_access_token
    nexus_client.auth.cookies.get("myqos_id") == refreshed_access_token  # type: ignore


@respx.mock
def test_token_refresh_expired() -> None:
    """Test the case of an expired refresh token, using in-memory token storage."""

    qnexus.consts.STORE_TOKENS = False

    write_token("refresh_token", "dummy_oat")
    write_token("access_token", "dummy_id")

    # Mock the list projects endpoint to force a refresh
    list_project_route = respx.get(f"{nexus_client.base_url}/api/projects/v1beta").mock(
        return_value=httpx.Response(401)
    )

    # Mock the expiry of the refresh token
    refresh_token_route = respx.post(
        f"{nexus_client.base_url}/auth/tokens/refresh"
    ).mock(return_value=httpx.Response(401))

    with pytest.raises(NotAuthenticatedException):
        projects.projects()

    assert list_project_route.called
    assert refresh_token_route.called
