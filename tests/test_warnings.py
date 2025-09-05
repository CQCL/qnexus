import typing
import warnings
from importlib.metadata import version
from unittest import mock

import httpx
import respx

import qnexus as qnx
from qnexus.client import (
    LATEST_VERSION_HEADER,
    VERSION_HEADER,
    VERSION_STATUS_HEADER,
    get_nexus_client,
)
from qnexus.client.utils import write_token

FAKE_LATEST_VERSION = "999.99.999-never-gonna-happen"
FAKE_VERSION_STATUS = "really bad"


@respx.mock
def test_sunset_header_emits_warning() -> None:
    fake_date = "foo"
    path = "/api/projects/v1beta2"
    list_project_route = respx.get(f"{get_nexus_client().base_url}{path}").mock(
        return_value=httpx.Response(
            status_code=200,
            json={"data": {}},
            headers={"Sunset": fake_date},
        )
    )

    with warnings.catch_warnings(record=True) as captured:
        qnx.projects.get_all().list()

    assert list_project_route.called
    assert len(captured) == 1
    assert captured[0].category is DeprecationWarning
    message = str(captured[0].message)
    assert fake_date in message
    assert "(" + path + ")" in message


def _check_version_warning_emitted(warning_msgs: list[warnings.WarningMessage]) -> None:
    """
    Assert that a warning has been emitted with all the properties we'd expect
    when we notify a user that they need to upgrade their client.
    """
    for warning_msg in warning_msgs:
        try:
            assert warning_msg.category is DeprecationWarning
            message = str(warning_msg.message)
            assert version("qnexus") in message
            assert FAKE_LATEST_VERSION in message
            assert FAKE_VERSION_STATUS in message
            assert "Please consider upgrading" in message
            return
        except AssertionError:
            pass  # on to the next warning, if any
    assert False, (
        f"The expected warning was not found (checked {len(warning_msgs)} warning messages)."
    )


def _check_request_includes_version_data(r: respx.Route) -> None:
    """
    Verify that a single call to a server URL has been made, and that it
    includes the expected version identifier header.
    """
    assert r.call_count == 1
    call: respx.models.Call = r.calls[0]
    headers: typing.MutableMapping[str, str] = call.request.headers
    assert headers[VERSION_HEADER] == version("qnexus")


@respx.mock
def test_version_check_emits_warning_refresh_token() -> None:
    """
    GIVEN: a server that includes a http header with a new version of qnexus
           and an indication that upgrade is advised
    WHEN:  the auth token is refreshed from an old version of qnexus
    THEN:  a warning is emitted, prompting the user to upgrade
    """
    write_token("refresh_token", "dummy_oat")

    # Mock the list projects endpoint to force a token refresh
    respx.get(f"{get_nexus_client().base_url}/api/projects/v1beta2").mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json={"included": {}, "data": []}),
        ]
    )

    # Mock the token refresh endpoint
    refresh_token_route = respx.post(
        f"{get_nexus_client().base_url}/auth/tokens/refresh"
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            headers={
                LATEST_VERSION_HEADER: FAKE_LATEST_VERSION,
                VERSION_STATUS_HEADER: "x;" + FAKE_VERSION_STATUS,
            },
        )
    )

    with warnings.catch_warnings(record=True) as captured:
        qnx.projects.get_all().list()

    _check_request_includes_version_data(refresh_token_route)
    _check_version_warning_emitted(captured)


@mock.patch("qnexus.client.auth.webbrowser")
@respx.mock
def test_version_check_emits_warning_login(m: mock.Mock) -> None:
    """
    GIVEN: a server that includes a http header with a new version of qnexus
           and an indication that upgrade is advised
    WHEN:  the login method is called from an old version of qnexus
    THEN:  a warning is emitted, prompting the user to upgrade
    """
    base_url = get_nexus_client().base_url

    # Mock the login endpoints
    respx.post(f"{base_url}/auth/device/device_authorization").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "user_code": "",
                "device_code": "",
                "verification_uri_complete": "https://example.com",
                "expires_in": 5,
                "interval": 1,
            },
        )
    )
    token_request_route = respx.post(f"{base_url}/auth/device/token").mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "refresh_token": "foo",
                "access_token": "bar",
                "email": "foo@example.com",
            },
            headers={
                LATEST_VERSION_HEADER: FAKE_LATEST_VERSION,
                VERSION_STATUS_HEADER: "x;" + FAKE_VERSION_STATUS,
            },
        )
    )

    with warnings.catch_warnings(record=True) as captured:
        qnx.login()

    _check_request_includes_version_data(token_request_route)
    _check_version_warning_emitted(captured)
