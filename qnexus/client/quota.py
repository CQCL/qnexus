"""Client API for quotas in Nexus."""
from typing import Literal

from qnexus.client import nexus_client
from qnexus.client.models import Quota
from qnexus.exceptions import ResourceFetchFailed
from qnexus.references import DataframableList

QuotaName = Literal["compilation", "simulation", "jupyterhub", "database_usage"]

_quota_map = {
    "compilation": "total_time_taken",
    "simulation": "total_time_taken",
    "jupyterhub": "total_time_taken",
    "database_usage": "megabytes_used",
}


def get() -> DataframableList[Quota]:
    """Get all quotas, including usage."""
    res = nexus_client.get(
        "/api/quotas/v1beta", params={"entity_type": "user", "include_usage": True}
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    quota_list: DataframableList[Quota] = DataframableList([])
    for quota in res.json():
        quota_key = _quota_map[quota["quota"]["name"]]
        quota_list.append(
            Quota(
                name=quota["quota"]["name"],
                description=quota["quota"]["details"]["description"],
                usage=quota["quota"]["usage"].get(quota_key, 0),
                quota=quota["quota"]["details"].get(quota_key, None),
            )
        )

    return quota_list


def get_only(name: QuotaName):
    """Get specific quota details by name."""
    res = nexus_client.get(
        "/api/quotas/v1beta",
        params={"entity_type": "user", "name": name, "include_usage": True},
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    quota = res.json()[0]

    quota_key = _quota_map[quota["quota"]["name"]]

    return Quota(
        name=quota["quota"]["name"],
        description=quota["quota"]["details"]["description"],
        usage=quota["quota"]["usage"].get(quota_key, None),
        quota=quota["quota"]["details"][quota_key],
    )


def check_quota(name: QuotaName) -> bool:
    """Check that the current user has available quota."""
    res = nexus_client.get("/api/quotas/v1beta/guard", params={"name": name})

    if res.status_code != 200:
        return False
    return True
