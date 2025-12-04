from collections.abc import Sequence
from datetime import datetime
from typing import Any

import httpx
from pact import Pact, match

PY_DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DT_STRING = "2025-10-21T11:23:47.489670Z"
DT_SAMPLE = datetime.strptime(DT_STRING, PY_DT_FORMAT)

PROJECT_DATA = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "attributes": {
        "contents_modified": DT_SAMPLE,
        "archived": False,
        "name": "project name",
        "description": "project description",
        "properties": {},
        "timestamps": {
            "created": DT_SAMPLE,
            "modified": DT_SAMPLE,
        },
    },
}

PROJECT_DATA_MATCHERS = {"id": match.uuid(str(PROJECT_DATA["id"])), "attributes": {}}


def _get_matcher_value(v: Any) -> match.AbstractMatcher[Any]:
    if isinstance(v, datetime):
        return match.datetime(DT_STRING, PY_DT_FORMAT)
    else:
        return match.type(v)


assert isinstance(PROJECT_DATA["attributes"], dict)
assert isinstance(PROJECT_DATA_MATCHERS["attributes"], dict)
for k, v in PROJECT_DATA["attributes"].items():
    if not isinstance(v, dict):
        PROJECT_DATA_MATCHERS["attributes"][k] = _get_matcher_value(v)
    else:
        PROJECT_DATA_MATCHERS["attributes"][k] = {}
        for k2, v2 in v.items():
            assert isinstance(PROJECT_DATA_MATCHERS["attributes"][k], dict)
            PROJECT_DATA_MATCHERS["attributes"][k][k2] = _get_matcher_value(v2)


PROJECT_RESPONSE = {
    "data": match.each_like(PROJECT_DATA_MATCHERS),
    "meta": {
        "page_number": match.integer(0, min=0),
        "page_size": match.integer(1, min=0),
        "total_pages": match.integer(1, min=0),
        "total_count": match.integer(1, min=0),
    },
}


def test_list_projects(pact: Pact) -> None:
    (
        pact.upon_receiving("a request to list projects")
        .with_request("GET", "/api/projects/v1beta2?scope=user")
        .will_respond_with(200)
        .with_body(PROJECT_RESPONSE)
    )

    with pact.serve() as srv:
        client = client = httpx.Client(base_url=str(srv.url), timeout=None)
        response = client.get("/api/projects/v1beta2?scope=user")
        response_data = response.json()["data"]

        # Check that the project response is the correct type
        assert isinstance(PROJECT_RESPONSE["data"], match.matcher.GenericMatcher)
        assert isinstance(PROJECT_RESPONSE["data"].value, Sequence)

        # Unlike PactJS, there is no "match.reify" function, so we have to get the sample values ourselves
        # Confirm that the response has the correct number of elements
        assert len(response_data) == len(PROJECT_RESPONSE["data"].value)

        # Check attribute values of the first response element
        assert "id" in response_data[0].keys()
        assert response_data[0]["id"] == PROJECT_DATA["id"]
        assert "attributes" in response_data[0].keys()
        for k, v in response_data[0]["attributes"].items():
            if not isinstance(v, dict):
                assert isinstance(PROJECT_DATA["attributes"], dict)
                _datetime_safe_assert(v, PROJECT_DATA["attributes"][k])
            else:
                assert isinstance(PROJECT_DATA["attributes"], dict)
                assert isinstance(PROJECT_DATA["attributes"][k], dict)
                # For each k2/v2 in project_data[attributes][k] (str/GenericMatcher)
                #     response_data[0][attributes][k][k2] == v2.value
                #     v = response_data[0][attributes][k]
                for k2, v2 in PROJECT_DATA["attributes"][k].items():
                    _datetime_safe_assert(v[k2], v2)


def _datetime_safe_assert(v1: str | datetime, v2: str | datetime) -> None:
    """
    Quick helper function to check if 2 values are the same, regardless of datetime/non-datetime conversions
    """
    if isinstance(v1, datetime):
        v1 = datetime.strftime(v1, PY_DT_FORMAT)
    if isinstance(v2, datetime):
        v2 = datetime.strftime(v2, PY_DT_FORMAT)
    assert v1 == v2
