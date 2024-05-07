""" """
from qnexus.client import nexus_client
from qnexus.client.pagination_iterator import RefList
from qnexus.exceptions import ResourceFetchFailed
from qnexus.references import DeviceRef

# Very much a TODO


def get() -> RefList:
    """"""
    res = nexus_client.get(
        "/api/v5/available_devices",
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    device_list = RefList([])

    for backendinfolist in res.json():
        for backend_info in backendinfolist["backend_info_list"]:
            device_list.append(
                DeviceRef(
                    backend_name=backend_info["name"],
                    device_name=backend_info["device_name"],
                    nexus_hosted=backendinfolist["is_local"],
                )
            )

    return device_list
