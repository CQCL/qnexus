"""Test the token-based auth logic for the httpx Client."""

import httpx
import pytest
import respx

import qnexus as qnx
from qnexus.client import get_nexus_client
from qnexus.client.utils import read_token, write_token
from qnexus.config import get_config
from qnexus.exceptions import AuthenticationError


@respx.mock
def test_token_refresh() -> None:
    """Test the auth refresh logic, using in-memory token storage."""

    get_config().store_tokens = False

    write_token("refresh_token", "dummy_oat")
    write_token("access_token", "dummy_id")
    refreshed_access_token = "new_dummy_id"

    # Mock the list projects endpoint to force a refresh
    list_project_route = respx.get(
        f"{get_nexus_client().base_url}/api/projects/v1beta"
    ).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json={"included": {}, "data": []}),
        ]
    )

    # Mock the refresh endpoint
    refresh_token_route = respx.post(
        f"{get_nexus_client().base_url}/auth/tokens/refresh"
    ).mock(
        return_value=httpx.Response(
            200,
            headers={
                "set-cookie": f"myqos_id={refreshed_access_token}; "
                "HttpOnly; Path=/; SameSite=Lax; Secure"
            },
        )
    )

    qnx.projects.get_all().list()

    assert list_project_route.called
    assert refresh_token_route.called

    # Confirm that the access token was updated
    assert read_token("access_token") == refreshed_access_token
    assert get_nexus_client().auth.cookies.get("myqos_id") == refreshed_access_token  # type: ignore


@respx.mock
def test_token_refresh_expired() -> None:
    """Test the case of an expired refresh token, using in-memory token storage."""

    get_config().store_tokens = False

    write_token("refresh_token", "dummy_oat")
    write_token("access_token", "dummy_id")

    # Mock the list projects endpoint to force a refresh
    list_project_route = respx.get(
        f"{get_nexus_client().base_url}/api/projects/v1beta"
    ).mock(return_value=httpx.Response(401))

    # Mock the expiry of the refresh token
    refresh_token_route = respx.post(
        f"{get_nexus_client().base_url}/auth/tokens/refresh"
    ).mock(return_value=httpx.Response(401))

    with pytest.raises(AuthenticationError):
        qnx.projects.get_all().list()

    assert list_project_route.called
    assert refresh_token_route.called
