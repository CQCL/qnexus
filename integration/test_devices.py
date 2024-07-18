"""Test basic functionality relating to the device module."""

import qnexus as qnx
from qnexus.models import Device
from qnexus.models.references import DataframableList


def test_device_get_all(
    _authenticated_nexus: None,
) -> None:
    """Test that we can get a list of devices."""
    devices = qnx.devices.get_all()
    assert isinstance(devices, DataframableList)

    for device in devices:
        assert isinstance(device, Device)
