"""Client API for devices in Nexus."""

from qnexus.client import nexus_client
from qnexus.client.models import Device
from qnexus.exceptions import ResourceFetchFailed
from qnexus.references import DataframableList

# work in progress


def get() -> DataframableList:
    """Get all available devices, work-in-progress."""
    res = nexus_client.get(
        "/api/v5/available_devices",
    )

    if res.status_code != 200:
        raise ResourceFetchFailed(message=res.json(), status_code=res.status_code)

    device_list = DataframableList([])

    for backendinfolist in res.json():
        for backend_info in backendinfolist["backend_info_list"]:
            device_list.append(
                Device(
                    backend_name=backend_info["name"],
                    device_name=backend_info["device_name"],
                    nexus_hosted=backendinfolist["is_local"],
                )
            )

    return device_list
