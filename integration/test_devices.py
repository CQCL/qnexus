"""Test basic functionality relating to the device module."""

import qnexus as qnx
from qnexus.client.models import Device
from qnexus.references import DataframableList


def test_device_get(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a list of devices."""
    devices = qnx.device.get()
    assert isinstance(devices, DataframableList)

    for device in devices:
        assert isinstance(device, Device)
