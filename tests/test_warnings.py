import warnings

import httpx
import respx

import qnexus as qnx
from qnexus.client import get_nexus_client


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
