import typing
import warnings
from importlib.metadata import version

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


@respx.mock
def test_sunset_header_emits_warning() -> None:
    fake_date = "foo"
    path = "/api/projects/v1beta"
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


@respx.mock
def test_qnexus_version_check_emits_warning() -> None:
    """
    GIVEN: a server that includes a http header with a new version of qnexus
           and an indication that upgrade is advised
    WHEN:  the auth token is refreshed from an old version of qnexus
    THEN:  a warning is emitted, prompting the user to upgrade
    """
    write_token("refresh_token", "dummy_oat")

    # Mock the list projects endpoint to force a refresh
    respx.get(f"{get_nexus_client().base_url}/api/projects/v1beta").mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json={"included": {}, "data": []}),
        ]
    )

    # Mock the refresh endpoint
    latest_version = "999.99.999-never-gonna-happen"
    version_status = "really bad"
    refresh_token_route = respx.post(
        f"{get_nexus_client().base_url}/auth/tokens/refresh"
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            headers={
                LATEST_VERSION_HEADER: latest_version,
                VERSION_STATUS_HEADER: "x;" + version_status,
            },
        )
    )

    with warnings.catch_warnings(record=True) as captured:
        qnx.projects.get_all().list()

    assert refresh_token_route.call_count == 1
    call: respx.models.Call = refresh_token_route.calls[0]
    headers: typing.MutableMapping[str, str] = call.request.headers
    assert headers[VERSION_HEADER] == version("qnexus")

    assert len(captured) == 1
    assert captured[0].category is DeprecationWarning
    message = str(captured[0].message)
    assert version("qnexus") in message
    assert latest_version in message
    assert version_status in message
    assert "Please consider upgrading" in message
